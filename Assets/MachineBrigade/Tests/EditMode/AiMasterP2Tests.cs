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
using MachineBrigade.Sim.Modes;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P2 (lane C, DECISIONS "AI MASTER P2 (lane C)"): role / mode intelligence and squad management. Part R rows
    /// R4 (fire support by mode), R5 (component damage), R6 (friendly firing lane), R7 (cover), the role-ladder side of R2 /
    /// R3, Part I26 (doctrine completeness), Part B ladders, and section 112's squad tests (reinforcement rendezvous,
    /// understrength merge, oversize split, narrow route / packets). Written by the lane, not run by it (the lead runs them).
    /// </summary>
    public class AiMasterP2Tests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        private static SimWorld Field(List<PropPlacement> props = null, float size = 300f, int seed = 5) =>
            new SimWorld(Catalog, new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                props ?? new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        /// <summary>The battle's mode tag (the mission goal cleared, which also drops the cached AI profile).</summary>
        private static void Mode(SimWorld world, string tag)
        {
            world.ModeTag = tag;
            world.MissionGoal = null;
        }

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

        private static AiCommander General(SimWorld world, Vector2 objective) =>
            new AiCommander(0, 1, AiSkill.For(AiDifficulty.Normal, Catalog.Ai), "balanced", w => objective);

        private static List<Vehicle> Pool(SimWorld world, int team = 0) =>
            world.Vehicles.Where(v => v.IsAlive && v.Team == team && !v.Flying && !v.Def.Static).ToList();

        private static void RunGeneral(SimWorld world, AiCommander general, float seconds, Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                general.Tick(world, TestWorlds.Step, Pool(world), null);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                each?.Invoke();
            }
        }

        // ================================================================== Part I26: doctrine completeness

        [Test]
        public void I26_EveryProfileGoalAndModeResolvesToADoctrine()
        {
            var missing = ModeCombatDoctrine.Validate(Catalog.AiModes);
            Assert.IsEmpty(missing, "every aiModeProfiles row, goal and mode maps to a ModeDoctrine: " + string.Join(", ", missing));
            foreach (var goal in Catalog.AiModes.Goals.Keys)
            {
                var id = ModeCombatDoctrine.Resolve(null, goal, Catalog.AiModes.For(null, goal), out var fallback);
                Assert.IsFalse(fallback, $"goal {goal} resolves without the fallback");
                Assert.IsTrue(ModeCombatDoctrine.Has(id), $"goal {goal} -> {id}");
            }
            foreach (var mode in Catalog.AiModes.Modes.Keys)
            {
                ModeCombatDoctrine.Resolve(mode, null, Catalog.AiModes.For(mode, null), out var fallback);
                Assert.IsFalse(fallback, $"mode {mode} resolves without the fallback");
            }
        }

        [Test]
        public void I26_AnUnknownProfileFallsBackToBalancedObjectiveNotNearestEnemy()
        {
            var id = ModeCombatDoctrine.Resolve("NoSuchMode", null, new AiModeProfile(), out var fallback);
            Assert.AreEqual("conquest", id, "the default profile id (conquest) has a doctrine");
            var unknown = ModeCombatDoctrine.Get("no_such_doctrine");
            Assert.AreEqual(ModeCombatDoctrine.Base, unknown.Id, "an unknown id plays BalancedObjectiveDoctrine");
            Assert.IsFalse(fallback);
        }

        [Test]
        public void I15_DoctrinesInheritAndDefendersPlayDefendWhileAttackersPlayAssault()
        {
            Assert.AreEqual("defend", ModeCombatDoctrine.Get("endless").Inherits, "Endless inherits Defend");
            Assert.AreEqual("siege", ModeCombatDoctrine.Get("weekly").Inherits, "Weekly inherits Siege");
            Assert.AreEqual("escort", ModeCombatDoctrine.Get("evacuate").Inherits, "Evacuate inherits Escort");
            var world = Field();
            Mode(world, "Siege"); // defender: the AI (team 1)
            world.Step(TestWorlds.Step);
            Assert.AreEqual("siege", world.Doctrine.For(0).Id, "the attacker plays Siege");
            Assert.AreEqual("defend", world.Doctrine.For(1).Id, "the fortress side plays Defend");
            world = Field();
            Mode(world, "Defend"); // defender: the player (team 0)
            world.Step(TestWorlds.Step);
            Assert.AreEqual(PursuitPolicy.NoChase, world.Doctrine.For(0).Pursuit, "the defender does not chase");
            Assert.AreEqual("assault", world.Doctrine.For(1).Id, "the wave side attacks");
        }

        // ================================================================== Part B ladders (B4-B13) and R2 / R3 regression

        [Test]
        public void B4_ATankDestroyerTakesTheSuperHeavyBeforeTheLightCar()
        {
            var td = CombatRoleDoctrine.Worth(DoctrineRole.TankDestroyer, TargetClass.SuperHeavy, false, 0f, false, false, false, 20f, false);
            var light = CombatRoleDoctrine.Worth(DoctrineRole.TankDestroyer, TargetClass.Light, false, 0f, false, false, false, 2f, false);
            var lightThreat = CombatRoleDoctrine.Worth(DoctrineRole.TankDestroyer, TargetClass.Light, true, 0f, false, false, false, 2f, false);
            Assert.Greater(td, light * 3f, "Pen5's purpose: Armour 5 first, a light car only as a last resort");
            Assert.Greater(lightThreat, light, "an immediately critical light target lifts the last resort");
        }

        [Test]
        public void B6_B7_B8_RoleLaddersRankTheirOwnTargetsFirst()
        {
            float W(DoctrineRole r, TargetClass c, bool cluster = false) => CombatRoleDoctrine.Worth(r, c, false, 0f, cluster, false, false, 8f, false);
            Assert.Greater(W(DoctrineRole.LightCombat, TargetClass.Light), W(DoctrineRole.LightCombat, TargetClass.Heavy), "B6: light first, heavy last");
            Assert.Greater(W(DoctrineRole.AntiAir, TargetClass.Bomber), W(DoctrineRole.AntiAir, TargetClass.Drone), "B7: bomber before drone");
            Assert.Greater(W(DoctrineRole.AntiAir, TargetClass.Helicopter), W(DoctrineRole.AntiAir, TargetClass.Mbt), "B7: no ground chase");
            Assert.Greater(W(DoctrineRole.FireSupport, TargetClass.Artillery), W(DoctrineRole.FireSupport, TargetClass.Tower), "B8: counter-battery first");
            Assert.Greater(W(DoctrineRole.FireSupport, TargetClass.Mbt, true), W(DoctrineRole.FireSupport, TargetClass.Light), "B8: a cluster before an isolated light");
            Assert.Greater(W(DoctrineRole.Fighter, TargetClass.Bomber), W(DoctrineRole.Fighter, TargetClass.Helicopter), "B12: bomber first");
            Assert.Greater(W(DoctrineRole.LoiterAntiArtillery, TargetClass.Artillery), W(DoctrineRole.LoiterAntiArtillery, TargetClass.Heavy), "B13 Lancet: artillery first");
            var salvo = CombatRoleDoctrine.Worth(DoctrineRole.FireSupport, TargetClass.Medium, false, 0f, false, false, false, 1f, true);
            Assert.AreEqual(SimTunables.Ai.RoleDoctrine.LastResort, salvo, 1e-4f, "B8: a heavy salvo keeps its minimum target value");
        }

        [Test]
        public void B4_InTheCombatScoreATankDestroyerPrefersTheHeavyTankToAScoutAtTheSameRange()
        {
            var world = Field();
            var td = world.SpawnVehicle("tank_destroyer", 0, Vector2.Zero, 0f);
            var heavy = Dummy(world, "heavy_tank", 1, new Vector2(-8f, 30f));
            var scout = Dummy(world, "scout_jeep", 1, new Vector2(8f, 30f));
            Run(world, 3f);
            Assert.AreEqual(heavy.Id, td.Target, "the TD's main gun is on the heavy, not the scout beside it");
            Assert.AreEqual(DoctrineRole.TankDestroyer, CombatRoleDoctrine.RoleOf(world, td));
            Assert.AreEqual(TargetClass.Recon, CombatRoleDoctrine.ClassOf(world, scout));
        }

        [Test]
        public void R2_R3_TheBreacherAndSiegeRowsStayP0AsAndTheLaddersLeaveThemAlone()
        {
            var world = Field();
            var dozer = world.SpawnVehicle("armored_bulldozer", 0, Vector2.Zero, 0f);
            var siege = world.SpawnVehicle("siege_tank", 0, new Vector2(10f, 0f), 0f);
            Assert.AreEqual(DoctrineRole.Breacher, CombatRoleDoctrine.BaseRole(world, dozer));
            Assert.AreEqual(DoctrineRole.Siege, CombatRoleDoctrine.BaseRole(world, siege));
            // The P2 role ladders return 1 for these roles: the B2 / B3 rows (P0-A's DoctrineWorth) decide.
            Assert.AreEqual(1f, CombatRoleDoctrine.Worth(DoctrineRole.Breacher, TargetClass.Light, false, 0f, false, false, false, 2f, false), 1e-6f);
            Assert.AreEqual(1f, CombatRoleDoctrine.Worth(DoctrineRole.Siege, TargetClass.Recon, false, 0f, false, false, false, 2f, false), 1e-6f);
        }

        [Test]
        public void I23_DestroyMissionTargetWeighsMoreForStrikeRoles()
        {
            var d = ModeCombatDoctrine.Get("destroy");
            var on = ModeCombatDoctrine.TargetWeight(d, ShowdownStage.None, DoctrineRole.FireSupport, TargetClass.Structure, true, false, false, 10f);
            var off = ModeCombatDoctrine.TargetWeight(d, ShowdownStage.None, DoctrineRole.FireSupport, TargetClass.Structure, false, false, false, 10f);
            Assert.Greater(on, off * 2f, "the mission structure is the strategic target");
            var shoot = ModeCombatDoctrine.Get("shootdown");
            Assert.Less(ModeCombatDoctrine.TargetWeight(shoot, ShowdownStage.None, DoctrineRole.AntiAir, TargetClass.Mbt, false, false, false, 10f), 1f,
                "ShootDown: an unrelated ground target weighs less");
            Assert.AreEqual(1f, ModeCombatDoctrine.TargetWeight(shoot, ShowdownStage.None, DoctrineRole.AntiAir, TargetClass.Mbt, false, true, false, 10f), 1e-5f,
                "unless it threatens the AA / objective");
        }

        // ================================================================== R4: fire support by mode

        private static readonly Vector2 Front = new(0f, 0f);
        private static readonly Vector2 Forward = new(0f, 1f);
        private static readonly Vector2 Objective = new(0f, 80f);

        private static FireSupportContext Ctx(Vector2? front = null, Vector2? objective = null, Vector2? enemy = null) =>
            new(front ?? Front, objective ?? Objective, Forward, enemy.HasValue, enemy, null);

        /// <summary>A side-0 battery of the given units behind the front, its director, the doctrine set by mode tag / goal.</summary>
        private static (SimWorld world, FireSupportDirector director, List<Vehicle> guns) Battery(string modeTag, string goal, params string[] units)
        {
            var world = Field();
            world.ModeTag = modeTag;
            world.MissionGoal = goal; // also drops the cached AI profile
            var guns = new List<Vehicle>();
            for (var i = 0; i < units.Length; i++) guns.Add(world.SpawnVehicle(units[i], 0, new Vector2(i * 12f - 12f, -40f), 0f));
            world.Step(TestWorlds.Step);
            return (world, new FireSupportDirector(0), guns);
        }

        private static FireSupportAnchorState Place(SimWorld world, FireSupportDirector director, Vehicle gun, List<Vehicle> guns, FireSupportContext ctx)
        {
            director.Stand(world, gun, guns, ctx);
            return director.AnchorOf(FireSupportDirector.ClassOf(world, gun));
        }

        private static void AssertInBand(FireSupportAnchorState a, string what)
        {
            var (min, max) = ModeCombatDoctrine.Band(a.Class);
            var lateral = SimTunables.Ai.FireSupport.LateralStep * SimTunables.Ai.FireSupport.LateralSamples;
            var d = Vector2.Distance(a.Point, a.Reference);
            Assert.That(d, Is.GreaterThanOrEqualTo(a.Point == a.Reference ? 0f : min * RangeOf(a) - 1f), what + ": not nearer than the band");
            Assert.That(d, Is.LessThanOrEqualTo(MathF.Sqrt(MathF.Pow(max * RangeOf(a), 2f) + lateral * lateral) + 1f), what + ": not farther than the band");
        }

        private static float RangeOf(FireSupportAnchorState a) => (float)typeof(FireSupportAnchorState)
            .GetField("Range", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)!.GetValue(a)!;

        [Test]
        public void R4_AssaultMortarAndMlrsAnchorInTheirBandsAndNotOnTheSquadCentroid()
        {
            var (world, director, guns) = Battery("Assault", null, "mortar_carrier", "mlrs");
            var mortar = Place(world, director, guns[0], guns, Ctx());
            var mlrs = Place(world, director, guns[1], guns, Ctx());
            Assert.AreEqual(FireClass.Mortar, mortar.Class);
            Assert.AreEqual(FireClass.Mlrs, mlrs.Class);
            Assert.AreEqual(FireSupportPolicy.FrontLogical, mortar.Policy);
            AssertInBand(mortar, "mortar 55-75 %");
            AssertInBand(mlrs, "MLRS 75-90 %");
            Assert.Greater(Vector2.Distance(mlrs.Point, mlrs.Reference), Vector2.Distance(mortar.Point, mortar.Reference), "MLRS deeper than the mortar");
            Assert.Greater(Vector2.Distance(mortar.Point, Front), 5f, "the anchor is not the squad centroid");
            Assert.IsTrue(Logged(world, P2Reasons.ArtilleryAnchorSet));
        }

        [Test]
        public void R4_DefendLaunchersDoNotMoveToMeetTheEnemy()
        {
            var (world, director, guns) = Battery("Defend", null, "mlrs");
            Assert.AreEqual(FireSupportPolicy.DefenceLine, world.Doctrine.For(0).FireSupport, "the defender (player side) holds a defence line");
            var first = Place(world, director, guns[0], guns, Ctx(enemy: new Vector2(0f, 160f))).Point;
            Run(world, 1f);
            // The enemy closes: the launcher's anchor does not move towards it (no pursuit; only a trigger moves it).
            var second = Place(world, director, guns[0], guns, Ctx(enemy: new Vector2(0f, 120f))).Point;
            Assert.LessOrEqual(second.Y, first.Y + 0.5f, "the anchor never steps towards the enemy");
            Assert.AreEqual(PursuitPolicy.NoChase, world.Doctrine.For(0).Pursuit);
        }

        [Test]
        public void R4_ConquestCoversTheObjectiveFromOutsideTheCircleAndRepositionsWhenItIsUncovered()
        {
            var (world, director, guns) = Battery("Conquest", null, "artillery");
            var a = Place(world, director, guns[0], guns, Ctx());
            Assert.AreEqual(FireSupportPolicy.ObjectiveCover, a.Policy);
            var d = Vector2.Distance(a.Point, Objective);
            Assert.That(d, Is.LessThanOrEqualTo(guns[0].Def.Weapon.Range).And.GreaterThan(15f), "covers the point from outside its circle");
            var sets = a.Sets;
            // A new objective far off: the old anchor no longer covers it.
            a = Place(world, director, guns[0], guns, Ctx(objective: new Vector2(120f, 120f)));
            Assert.Greater(a.Sets, sets, "repositioned");
            Assert.That(new[] { "rangeBandLost", "objectiveUncovered" }, Does.Contain(a.Reason));
        }

        [Test]
        public void R4_EscortFireSupportLeapfrogsAheadOfTheConvoyAndIsNotGluedToIt()
        {
            var (world, director, guns) = Battery("Operation", "Escort", "mortar_carrier");
            var convoy = new Vector2(0f, 10f);
            world.ConvoySafeZone = () => new[] { convoy };
            world.Step(TestWorlds.Step);
            var a = Place(world, director, guns[0], guns, Ctx());
            Assert.AreEqual(FireSupportPolicy.ConvoyLeapfrog, a.Policy);
            Assert.Greater(Vector2.Distance(a.Point, convoy), 8f, "not glued to the convoy");
            Assert.AreEqual(PursuitPolicy.Leash, world.Doctrine.For(0).Pursuit, "the escort leash beats pursuit");
        }

        [Test]
        public void R4_SiegeLayersMortarClosestMlrsFartherWithShootAndScoot()
        {
            var (world, director, guns) = Battery("Siege", null, "mortar_carrier", "mlrs", "heavy_rocket_artillery");
            var mortar = Place(world, director, guns[0], guns, Ctx());
            var mlrs = Place(world, director, guns[1], guns, Ctx());
            var heavy = Place(world, director, guns[2], guns, Ctx());
            Assert.AreEqual(FireSupportPolicy.SiegeLayers, mortar.Policy);
            Assert.IsTrue(world.Doctrine.For(0).ShootAndScoot);
            var dm = Vector2.Distance(mortar.Point, mortar.Reference);
            var dl = Vector2.Distance(mlrs.Point, mlrs.Reference);
            var dh = Vector2.Distance(heavy.Point, heavy.Reference);
            Assert.That(dm < dl && dl < dh, $"mortar {dm:0} < MLRS {dl:0} < heavy {dh:0}");
        }

        [Test]
        public void R4_SurvivalPreparesPocketsAndRotatesThem()
        {
            var (world, director, guns) = Battery("Survival", null, "mortar_carrier");
            var a = Place(world, director, guns[0], guns, Ctx(enemy: new Vector2(0f, 150f)));
            Assert.AreEqual(FireSupportPolicy.PreparedPockets, a.Policy);
            var first = a.Point;
            Run(world, SimTunables.Ai.ModeDoctrine.RotateSeconds + 1f);
            a = Place(world, director, guns[0], guns, Ctx(enemy: new Vector2(0f, 150f)));
            Assert.AreEqual("rotation", a.Reason, "the pocket rotates");
            Assert.Greater(Vector2.Distance(first, a.Point), 5f, "to another prepared pocket");
            Assert.AreEqual(PursuitPolicy.NoChase, world.Doctrine.For(0).Pursuit, "survival: no chase");
        }

        [Test]
        public void R4_BossRushPredictsTheBossRegionInsteadOfFollowingIt()
        {
            var (world, director, guns) = Battery("BossRush", null, "artillery");
            var boss = world.SpawnVehicle("behemoth", 1, new Vector2(0f, 50f), MathF.PI);
            Run(world, 1f);
            var a = Place(world, director, guns[0], guns, Ctx(enemy: boss.Position));
            Assert.AreEqual(FireSupportPolicy.BossPredict, a.Policy);
            Assert.Greater(Vector2.Distance(a.Point, boss.Position), guns[0].Def.Weapon.MinRange, "outside its minimum reach, not chasing the boss");
            Assert.LessOrEqual(Vector2.Distance(a.Point, a.Reference), guns[0].Def.Weapon.Range + 1f, "the predicted region stays in reach");
        }

        [Test]
        public void R4_DeathmatchRepositionsWhenTheFrontMovesOutOfTheBand()
        {
            var (world, director, guns) = Battery("Deathmatch", null, "mortar_carrier");
            var a = Place(world, director, guns[0], guns, Ctx());
            Assert.AreEqual(FireSupportPolicy.FrontLogical, a.Policy);
            var sets = a.Sets;
            a = Place(world, director, guns[0], guns, Ctx(front: new Vector2(0f, 90f), objective: new Vector2(0f, 170f)));
            Assert.Greater(a.Sets, sets, "the front moved past the useful band: reposition");
        }

        [Test]
        public void R4_HuntLaunchersStandBehindTheFrontNeverChasing()
        {
            var (world, director, guns) = Battery("Operation", "Hunt", "mlrs");
            var a = Place(world, director, guns[0], guns, Ctx(enemy: new Vector2(10f, 60f)));
            Assert.AreEqual(FireSupportPolicy.InterceptPredict, a.Policy);
            Assert.Less(Vector2.Dot(a.Point - Front, Forward), 0.5f, "the launcher stays at or behind the front");
        }

        [Test]
        public void R4_OperationPhaseTransitionRebuildsTheAnchor()
        {
            var (world, director, guns) = Battery("Operation", null, "artillery");
            var a = Place(world, director, guns[0], guns, Ctx());
            var gen = world.Doctrine.Generation;
            world.SetAiPhase("phase:2");
            world.Step(TestWorlds.Step);
            a = Place(world, director, guns[0], guns, Ctx());
            Assert.Greater(world.Doctrine.Generation, gen, "the phase bumps the doctrine generation");
            Assert.AreEqual("phase", a.Reason, "the anchor is rebuilt for the new phase (no stale doctrine)");
            Assert.IsTrue(Logged(world, P2Reasons.ModePhaseRebuild));
        }

        [Test]
        public void R4_ShowdownEarlyDeepFinalForward()
        {
            var (world, director, guns) = Battery("Showdown", null, "artillery");
            world.Intel.Objectives = new ShowdownMode(new ShowdownRules { EscalationAt = 1f, RebuildCutoff = 2f });
            world.Step(TestWorlds.Step);
            Assert.AreEqual(ShowdownStage.Early, world.Doctrine.Stage);
            var first = Place(world, director, guns[0], guns, Ctx());
            var early = Vector2.Distance(first.Point, first.Reference);
            Run(world, 2.2f);
            Assert.AreEqual(ShowdownStage.Final, world.Doctrine.Stage);
            var a = Place(world, director, guns[0], guns, Ctx());
            Assert.AreEqual("phase", a.Reason);
            Assert.Less(Vector2.Distance(a.Point, a.Reference), early + 1f, "the final stage moves forward only to keep its value");
            Assert.AreEqual((0f, SimTunables.Ai.ModeDoctrine.FinalReserveShare), world.Doctrine.ReserveShareOf(0), "and cuts the reserve");
        }

        // ================================================================== R5: component damage

        [Test]
        public void R5_AnMbtThatLosesItsMainGunBecomesAScreenWithoutAHealthRetreat()
        {
            var world = Field();
            var objective = new Vector2(0f, 90f);
            var general = General(world, objective);
            var tanks = new List<Vehicle>();
            for (var i = 0; i < 4; i++) tanks.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 7f, 0f), 0f));
            RunGeneral(world, general, 2f);
            var tank = tanks[0];
            var squad = general.Squads.SquadOf(tank.Id);
            Assert.IsNotNull(squad);
            Assert.AreEqual(Placement.Front, SquadLayer.PlacementOf(world, tank, false));
            // The main gun's mount is out for good (its part broken); its health is untouched.
            tank.MountOff = new bool[tank.Def.Mounts.Count];
            tank.MountOff[0] = true;
            var hp = tank.Hp;
            RunGeneral(world, general, 2f);
            Assert.AreEqual(DoctrineRole.Screen, CombatRoleDoctrine.RoleOf(world, tank), "the role changes (F1)");
            Assert.AreNotEqual(Placement.Front, SquadLayer.PlacementOf(world, tank, false), "off the front row");
            Assert.IsTrue(Logged(world, P2Reasons.RoleMainGunLost));
            Assert.AreEqual(squad.Id, general.Squads.SquadOf(tank.Id)?.Id, "it stays in its squad: no retreat");
            Assert.AreEqual(hp, tank.Hp, 1e-3f);
        }

        [Test]
        public void R5_ABossThatLosesABatteryDropsItsHeldBroadsideAndRecomputes()
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("lighthousebay_sandbox"), 13);
            world.SeaRules.FleetShare = 0f;
            var sea = world.Map.Sea;
            var boss = world.SpawnVehicle("leviathan", 1, sea.At(-40f, sea.Lane("mid").W), MachineBrigade.Sim.Core.SimMath.HeadingOf(sea.Along));
            Run(world, 1f);
            Assume.That(boss.BossBrain, Is.Not.Null);
            var part = -1;
            for (var i = 0; i < boss.Def.Parts.Count && part < 0; i++)
                if (boss.Def.Parts[i].Mounts.Count > 0) part = i;
            Assume.That(part >= 0);
            world.Bosses.Break(boss, part);
            Run(world, 1f);
            Assert.IsTrue(Logged(world, P2Reasons.BossBroadsideRecompute), "the broken battery forces a broadside recompute (F5)");
        }

        // ================================================================== R6: friendly firing lane

        [Test]
        public void R6_TheRearTankSidestepsThenTakesAnEquivalentSlotInsteadOfIdling()
        {
            var world = Field();
            var rear = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var front = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 9f), 0f);
            rear.HoldFire = true;
            front.HoldFire = true;
            var enemy = Dummy(world, "light_tank", 1, new Vector2(0f, 30f));
            world.Step(TestWorlds.Step);
            var lanes = world.FiringLanes;
            Assert.AreEqual(front.Id, lanes.Blocker(rear, enemy.Position)?.Id, "the front tank blocks the rear one's line");
            Assert.AreEqual(LaneResolution.None, lanes.Resolve(front, enemy.Position, out _, out _), "the front tank is not blocked (no oscillation)");
            var first = lanes.Resolve(rear, enemy.Position, out var step, out _);
            Assert.AreEqual(LaneResolution.Sidestep, first, "E2 step 2: a small sidestep (the blocker stands)");
            Assert.Greater(MathF.Abs(step.X), 2.5f, "lateral, and clear of the blocker's line (the resolver checks it)");
            Run(world, SimTunables.Ai.FiringLane.CooldownSeconds + 0.2f);
            var second = lanes.Resolve(rear, enemy.Position, out var slot, out _);
            Assert.AreEqual(LaneResolution.AlternateSlot, second, "E2 step 3: the equivalent slot");
            Assert.AreEqual(Vector2.Distance(rear.Position, enemy.Position), Vector2.Distance(slot, enemy.Position), 1.5f, "same distance to the target");
            Run(world, SimTunables.Ai.FiringLane.CooldownSeconds + 0.2f);
            Assert.AreEqual(LaneResolution.Retarget, lanes.Resolve(rear, enemy.Position, out _, out _), "E2 step 4: another target");
            Run(world, SimTunables.Ai.FiringLane.CooldownSeconds + 0.2f);
            Assert.AreEqual(LaneResolution.MoveBlocker, lanes.Resolve(rear, enemy.Position, out _, out var blocker), "E2 step 5: the idle blocker steps aside");
            Assert.AreEqual(front.Id, blocker?.Id);
            Assert.AreEqual(LaneResolution.None, lanes.Resolve(front, enemy.Position, out _, out _), "the blocker itself is never sent round the ladder");
            Assert.IsTrue(Logged(world, P2Reasons.PositionFriendlyBlock));
        }

        [Test]
        public void R6_InARunTheBlockedRearTankFiresOrMovesAndNeverIdlesUnexplained()
        {
            var world = Field();
            var ai = new TacticalAi(0, 1);
            var rear = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var front = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 9f), 0f);
            front.HoldFire = true;
            Dummy(world, "light_tank", 1, new Vector2(0f, 26f));
            var start = rear.Position;
            Run(world, 14f, () => ai.Tick(world, TestWorlds.Step));
            Assert.That(rear.LastFiredAt > 0.0 || Vector2.Distance(rear.Position, start) > 2f, "it fires or steps out of the lane");
            Assert.AreEqual(0, world.CombatWatch.Unexplained, "never a silent idle");
        }

        // ================================================================== R7: cover

        [Test]
        public void R7_ATankDestroyerPrefersTheHullDownSpotToOpenGroundWithTheSameTiming()
        {
            var props = new List<PropPlacement> { new("sandbags", new Vector2(0f, 10f), 0) };
            var world = Field(props);
            var td = world.SpawnVehicle("tank_destroyer", 0, new Vector2(4f, 6f), 0f);
            var enemy = Dummy(world, "main_battle_tank", 1, new Vector2(0f, 36f));
            world.Step(TestWorlds.Step);
            Assume.That(td.Def.Weapon.Range, Is.GreaterThan(32f));
            var hullDown = new Vector2(0f, 5f);
            var open = new Vector2(20f, 5f);
            Assert.IsTrue(FiringPositionScorer.HullDown(world, hullDown, enemy.Position, enemy.Position), "low cover in front, the target still in a clear line");
            Assert.IsFalse(FiringPositionScorer.HullDown(world, open, enemy.Position, enemy.Position));
            var h = FiringPositionScorer.Score(world, td, hullDown, enemy.Position, enemy.Position, DoctrineRole.TankDestroyer, out var th);
            var o = FiringPositionScorer.Score(world, td, open, enemy.Position, enemy.Position, DoctrineRole.TankDestroyer, out var to);
            Assert.AreEqual(to.Uptime, th.Uptime, "equivalent firing (mission timing)");
            Assert.Greater(h, o, $"hull-down preferred ({th} vs {to})");
            var best = FiringPositionScorer.Best(world, td, td.Position, enemy.Position, enemy.Position, DoctrineRole.TankDestroyer);
            Assert.IsTrue(FiringPositionScorer.HullDown(world, best, enemy.Position, enemy.Position), "the search near its slot finds the hull-down spot");
            Assert.IsTrue(Logged(world, P2Reasons.PositionHullDown));
            // D5: another TD does not take the same reserved point.
            var other = world.SpawnVehicle("tank_destroyer", 0, new Vector2(-4f, 6f), 0f);
            Assert.IsTrue(world.Positions.ReservedByOther(best, other.Id), "the spot is reserved for the first");
        }

        // ================================================================== section 112: squads

        [Test]
        public void S112_AReinforcementGoesToARendezvousBehindTheSquadAndJoinsThere()
        {
            var world = Field();
            Mode(world, "Siege"); // no reserve (the squads stay on one task)
            var objective = new Vector2(0f, 120f);
            var general = General(world, objective);
            for (var i = 0; i < 5; i++) world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 7f - 14f, 0f), 0f);
            RunGeneral(world, general, 2f);
            var squad = general.Squads.Squads.Single(s => s.MemberList.Count > 0);
            var late = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -110f), 0f);
            RunGeneral(world, general, 1.1f);
            Assert.AreEqual(squad.Id, general.Squads.SquadOf(late.Id)?.Id, "it reinforces the squad of its kind");
            var pending = squad.Pending.SingleOrDefault(p => p.Id == late.Id);
            Assert.AreEqual(late.Id, pending.Id, "on its way to a rendezvous first");
            Assert.Greater(Vector2.Distance(pending.Rendezvous, squad.Centre), 8f, "not the squad leader / centroid");
            Assert.IsTrue(Logged(world, P2Reasons.SquadReinforcementPending));
            var joined = false;
            RunGeneral(world, general, 60f, () => joined |= squad.Members.Contains(late.Id));
            Assert.IsTrue(joined, "received within 12-20 m");
            Assert.IsTrue(Logged(world, P2Reasons.SquadReinforcementJoined));
        }

        [Test]
        public void S112_AnUnderstrengthSquadMergesIntoACompatibleOne()
        {
            var world = Field();
            Mode(world, "Siege");
            var general = General(world, new Vector2(0f, 120f));
            for (var i = 0; i < 7; i++) world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f - 18f, 0f), 0f);
            RunGeneral(world, general, 1.1f);
            for (var i = 0; i < 2; i++) world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f, -18f), 0f);
            RunGeneral(world, general, 10f);
            var squads = general.Squads.Squads.Where(s => s.MemberList.Count > 0).ToList();
            Assert.AreEqual(1, squads.Count, "the two-tank squad (under 45 % of desired) merged");
            Assert.AreEqual(9, squads[0].MemberList.Count, "up to the maximum of 9");
            Assert.IsTrue(Logged(world, P2Reasons.SquadMerge));
        }

        [Test]
        public void S112_MergeRulesRefuseReserveOppositeFlankFarAndOversize()
        {
            var world = Field();
            var general = General(world, new Vector2(0f, 120f));
            var layer = general.Squads;
            var intel = world.Intel.For(0);
            var a = layer.Form(world, Enumerable.Range(0, 5).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f, 0f), 0f)).ToList());
            var b = layer.Form(world, Enumerable.Range(0, 2).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f, 20f), 0f)).ToList());
            Assert.IsTrue(SquadLayer.Understrength(world, b));
            Assert.IsTrue(layer.CanMerge(world, intel, a, b, SimTunables.Ai.Squads.MergeDistance, true), "understrength, close, compatible, no combat");
            b.Task = new SquadTask { Kind = TaskKind.Reserve };
            Assert.IsFalse(layer.CanMerge(world, intel, a, b, 35f, true), "never a reserve");
            b.Task = default;
            a.Action = SquadAction.FlankLeft;
            b.Action = SquadAction.FlankRight;
            Assert.IsFalse(layer.CanMerge(world, intel, a, b, 35f, true), "never opposite flanks");
            a.Action = b.Action = SquadAction.Attack;
            Assert.IsFalse(layer.CanMerge(world, intel, a, b, 10f, true), "not past the distance");
            var c = layer.Form(world, Enumerable.Range(0, 5).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f, -20f), 0f)).ToList());
            Assert.IsFalse(layer.CanMerge(world, intel, a, c, 35f, true), "two healthy squads do not merge");
        }

        [Test]
        public void S112_AnOversizedSquadSplits()
        {
            var world = Field();
            Mode(world, "Siege");
            var general = General(world, new Vector2(0f, 120f));
            var layer = general.Squads;
            var squad = layer.Form(world, Enumerable.Range(0, 11).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i % 4 * 6f, i / 4 * 6f), 0f)).ToList());
            RunGeneral(world, general, 0.6f);
            Assert.LessOrEqual(squad.MemberList.Count, SquadLayer.MaxSquad, "no squad over 9");
            Assert.GreaterOrEqual(layer.Squads.Count(s => s.MemberList.Count > 0), 2, "split in two");
            Assert.IsTrue(Logged(world, P2Reasons.SquadSplit));
        }

        private static List<PropPlacement> Gap() => new()
        {
            // Two cliffs leaving a ~6 m gap at x = 0, y = 30.
            new PropPlacement("cliff_a", new Vector2(-9.5f, 30f), 0),
            new PropPlacement("cliff_a", new Vector2(9.5f, 30f), 0),
            new PropPlacement("cliff_a", new Vector2(-22.5f, 30f), 0),
            new PropPlacement("cliff_a", new Vector2(22.5f, 30f), 0),
        };

        [Test]
        public void S112_NarrowRouteSwitchesToTheTravelColumnAndPacketsGoInTurns()
        {
            var world = Field(Gap());
            Mode(world, "Siege");
            Assume.That(world.Topology.Chokes.Count, Is.GreaterThan(0), "the gap is a choke");
            var general = General(world, new Vector2(0f, 120f));
            var layer = general.Squads;
            var squad = layer.Form(world, Enumerable.Range(0, 6).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 7f - 17f, 10f), 0f)).ToList());
            // Flanking (wide echelon), heading through the gap.
            squad.Action = SquadAction.FlankRight;
            squad.State = SquadState.Flank;
            squad.Formation = FormationMode.Flank;
            layer.ChooseFormation(world, world.Intel.For(0), squad, new Vector2(0f, 60f));
            Assert.AreEqual(FormationMode.Travel, squad.Formation, "formation -> travel column before the choke (86)");
            Assert.AreEqual(P2Reasons.FormationChokeTravel, squad.FormationReason);
            layer.SlotsP2(world, squad, new Vector2(0f, 60f), new Vector2(0f, 1f), FormationMode.Travel, CommandType.Move);
            Assert.IsTrue(squad.ColumnOrder.Count == 6, "a stable column");
            Assert.IsTrue(Logged(world, P2Reasons.FormationPackets), "the back packet waits (spec 22: 2-4 s apart)");
            var waiting = squad.MemberList.Count(id => squad.ReleaseAt.TryGetValue(id, out var at) && at > world.Time);
            Assert.Greater(waiting, 0);
        }

        [Test]
        public void S160_S161_SlotsAndColumnOrderAreStable()
        {
            var world = Field();
            var general = General(world, new Vector2(0f, 120f));
            var layer = general.Squads;
            var units = new List<Vehicle>
            {
                world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f),
                world.SpawnVehicle("heavy_tank", 0, new Vector2(6f, 0f), 0f),
                world.SpawnVehicle("aa_vehicle", 0, new Vector2(12f, 0f), 0f),
                world.SpawnVehicle("ifv", 0, new Vector2(18f, 0f), 0f),
            };
            var squad = layer.Form(world, units);
            layer.SlotsP2(world, squad, new Vector2(0f, 60f), new Vector2(0f, 1f), FormationMode.Travel, CommandType.Move);
            var column = squad.ColumnOrder.ToList();
            Assert.AreEqual(units[1].Id, column[0], "heavy leads the column (27)");
            Assert.AreEqual(units[2].Id, column[column.Count - 1], "AA at the rear, never front");
            layer.SlotsP2(world, squad, new Vector2(0f, 64f), new Vector2(0f, 1f), FormationMode.Travel, CommandType.Move);
            CollectionAssert.AreEqual(column, squad.ColumnOrder.ToList(), "no reorder without a member change (161)");
            layer.SlotsP2(world, squad, new Vector2(0f, 60f), new Vector2(0f, 1f), FormationMode.Hold, CommandType.Move);
            var slots = new Dictionary<EntityId, int>(squad.SlotOf);
            layer.SlotsP2(world, squad, new Vector2(0f, 61f), new Vector2(0f, 1f), FormationMode.Hold, CommandType.Move);
            CollectionAssert.AreEquivalent(slots, squad.SlotOf, "members keep their slots (160)");
        }

        [Test]
        public void S25_CohesionIsLowWhenScatteredAndHighWhenGathered()
        {
            var world = Field();
            var general = General(world, new Vector2(0f, 120f));
            var layer = general.Squads;
            var tight = layer.Form(world, Enumerable.Range(0, 4).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 6f, 0f), 0f)).ToList());
            var loose = layer.Form(world, Enumerable.Range(0, 4).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(i * 45f - 60f, -90f), 0f)).ToList());
            Assert.Greater(tight.Cohesion, SimTunables.Ai.Squads.CohesionRegroup, "gathered");
            Assert.Less(loose.Cohesion, SimTunables.Ai.Squads.CohesionRegroup, "scattered: under 0.55");
        }

        [Test]
        public void S24_TheCommanderKeepsAReserveWhereTheModeAllowsIt()
        {
            var world = Field();
            Mode(world, "Conquest");
            var general = General(world, new Vector2(0f, 120f));
            // Two full squads of 7 and a small one of 3 (3/17 = 18 %: inside the 15-25 % band).
            for (var i = 0; i < 17; i++) world.SpawnVehicle("main_battle_tank", 0, new Vector2(i % 7 * 6f - 18f, i / 7 * 40f), 0f);
            RunGeneral(world, general, 2.2f);
            var squads = general.Squads.Squads.Where(s => s.MemberList.Count > 0).ToList();
            Assume.That(squads.Count, Is.GreaterThanOrEqualTo(2));
            var total = squads.Sum(s => s.Strength);
            var reserve = squads.Where(s => s.IsReserve).Sum(s => s.Strength);
            Assert.Greater(reserve, 0f, "a reserve is kept");
            Assert.LessOrEqual(reserve, total * SimTunables.Ai.ModeDoctrine.ReserveShare[1] + 1e-3f, "at most 25 %");
        }
    }
}
