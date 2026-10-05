using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P3 (lane A, DECISIONS "AI MASTER P3 (lane A)"): the coordination layer's rows of Part R / section 224 -
    /// death memory, scout-before-commit, fix-and-flank, counter-battery confidence, shoot-and-scoot, pursuit leash, objective
    /// deadline, counterattack opportunity, synchronized ETA - plus route diversity, reserve release, the planned action
    /// board (damage / repair / smoke), confidence (not morale), stances, range margin and defence in depth. The rules are
    /// tested on the P3 classes the commander and squads call (deterministic, no world needed). Written by the lane, not run
    /// by it (the lead runs them).
    /// </summary>
    [Category("AIMasterP3")]
    public class AiMasterP3Tests
    {
        [SetUp]
        public void SetUp() => SimTunables.Reset();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        private static float Cost(TacticalMemory memory, Vector2 from, Vector2 via, Vector2 to, double now) =>
            RouteDiversity.Cost(Vector2.Distance(from, via) + Vector2.Distance(via, to), 0f, 0f, 0,
                System.MathF.Max(memory.DeathAlong(from, via, now), memory.DeathAlong(via, to, now)), 0f);

        // ------------------------------------------------------------------------------------------------ 224 death memory

        [Test]
        public void S224_DeathMemory_ASquadKilledAtTheChokeMakesTheNextScoutOrTakeTheOtherRoute()
        {
            var memory = new TacticalMemory();
            Vector2 from = new(0f, 0f), to = new(100f, 0f), choke = new(50f, 0f), detour = new(50f, 40f);
            // Two 15 CP tanks lost in the choke at t = 10.
            memory.AddDeath(choke, 15f, 10.0);
            memory.AddDeath(choke + new Vector2(2f, 0f), 15f, 10.5);
            var now = 12.0;
            Assert.Greater(memory.DeathDanger(choke, now), 2f, "the kill zone is marked");
            Assert.AreEqual(0f, memory.DeathDanger(detour, now), 1e-4f, "only near the losses");
            var through = Cost(memory, from, choke, to, now);
            var round = Cost(memory, from, detour, to, now);
            Assert.Less(round, through, "the next squad's route cost avoids the kill zone");
            var book = new RouteBook();
            Assert.AreEqual(1, RouteDiversity.Choose(new[] { through, round }, new[] { choke, detour }, book, 2, now), "no blind push through the choke");
            Assert.IsTrue(ScoutPlanner.Needed(0f, memory.DeathDanger(choke, now), 0f, false), "the losses raise scout demand");
            // Not a permanent fear (no morale): two minutes later the short route is the best again.
            var later = 130.0;
            Assert.Less(Cost(memory, from, choke, to, later), Cost(memory, from, detour, to, later));
        }

        // ------------------------------------------------------------------------------------------------ 131

        [Test]
        public void S131_ScoutBeforeCommit_UnknownGroundAsksAScoutAndTheWaitIsCapped()
        {
            Assert.IsTrue(ScoutPlanner.Needed(0.8f, 0f, 0f, false), "mostly unknown ground");
            Assert.IsFalse(ScoutPlanner.Needed(0.1f, 0.1f, 0f, false), "known, quiet ground: commit");
            Assert.IsFalse(ScoutPlanner.Needed(0.8f, 3f, 0.9f, false), "an emergency objective beats scouting (226)");
            Assert.IsFalse(ScoutPlanner.Needed(0.8f, 3f, 0f, true), "a short match timer drops scout-before-commit (226)");
            Assert.AreEqual(2f, ScoutPlanner.Wait(1f), 1e-4f, "at least 2 s");
            Assert.AreEqual(4f, ScoutPlanner.Wait(4f), 1e-4f);
            Assert.AreEqual(SimTunables.Ai.AttackSync.ScoutMaxWaitS, ScoutPlanner.Wait(30f), 1e-4f, "never waits forever");
        }

        // ------------------------------------------------------------------------------------------------ 134

        [Test]
        public void S134_FixAndFlank_NeedsAStableClusterTwoRoutesAndPowerAndTheFixDoesNotCloseIn()
        {
            Assert.IsTrue(FixAndFlank.Viable(true, 2, 10f, 8f, 1.2f));
            Assert.IsFalse(FixAndFlank.Viable(true, 1, 10f, 8f, 1.2f), "one access route");
            Assert.IsFalse(FixAndFlank.Viable(false, 3, 10f, 8f, 1.2f), "the enemy is on the move");
            Assert.IsFalse(FixAndFlank.Viable(true, 3, 5f, 8f, 1.2f), "not enough power");
            Vector2 from = new(0f, 0f), target = new(100f, 0f);
            var goal = FixAndFlank.FixGoal(from, target, new Vector2(95f, 0f), 40f);
            Assert.GreaterOrEqual(Vector2.Distance(goal, target), 40f * SimTunables.Ai.AttackSync.FixEnvelope - 0.01f, "the fix keeps its envelope");
            var far = new Vector2(50f, 0f);
            Assert.AreEqual(far, FixAndFlank.FixGoal(from, target, far, 40f), "a goal already outside the envelope is kept");
        }

        // ------------------------------------------------------------------------------------------------ 224 counterbattery

        [Test]
        public void S224_Counterbattery_ShotsFromOneAreaRaiseConfidenceShrinkTheErrorAndMakeAMission()
        {
            var tracker = new CounterBatteryTracker();
            Vector2 origin = new(200f, 200f), impact = new(50f, 60f);
            var flight = Vector2.Distance(origin, impact);
            var last = 0f;
            var error = float.MaxValue;
            for (var shot = 0; shot < 5; shot++)
            {
                var e = tracker.Observe(origin, impact + new Vector2(shot, 0f), 1000 + shot * 7, 10.0 + shot);
                var c = e.Confidence(10.0 + shot);
                Assert.Greater(c, last, "every shot from the same area adds confidence");
                Assert.LessOrEqual(e.ErrorRadius, error, "the error shrinks with the shots");
                Assert.GreaterOrEqual(e.ErrorRadius, SimTunables.Ai.FireMissions.MinError - 1e-4f, "never a perfect origin");
                Assert.LessOrEqual(Vector2.Distance(e.Centre, origin), flight * SimTunables.Ai.FireMissions.ErrorShare + 1e-3f, "inside the first error radius");
                last = c;
                error = e.ErrorRadius;
            }
            Assert.AreEqual(1, tracker.Estimates.Count, "one battery");
            Assert.IsNotNull(tracker.Best(14.0, SimTunables.Ai.FireMissions.MissionConfidence), "a counter-battery mission");
            Assert.Less(tracker.Estimates[0].Confidence(74.0), tracker.Estimates[0].Confidence(14.0), "confidence fades without new shots");
            var single = new CounterBatteryTracker();
            single.Observe(origin, impact, 5, 0.0);
            Assert.IsNull(single.Best(0.0, SimTunables.Ai.FireMissions.MissionConfidence), "one shot is not enough");
            tracker.Observe(new Vector2(-200f, -200f), impact, 77, 15.0);
            Assert.AreEqual(2, tracker.Estimates.Count, "a second area is a second battery");
        }

        // ------------------------------------------------------------------------------------------------ 145

        [Test]
        public void S145_ShootAndScoot_AfterTwoToFourSalvosOrAtOnceUnderCounterBatteryThreat()
        {
            var salvos = new HashSet<int>();
            for (var id = 1; id <= 30; id++)
            {
                var n = ShootAndScoot.Salvos(id);
                Assert.That(n, Is.InRange(2, 4));
                salvos.Add(n);
                Assert.That(ShootAndScoot.Distance(id), Is.InRange(12f, 30f));
                Assert.IsTrue(ShootAndScoot.Due(n, id, false, true), "scoot after its salvos when enemy artillery is known");
                Assert.IsFalse(ShootAndScoot.Due(n, id, false, false), "no enemy artillery known: no scoot");
                Assert.IsTrue(ShootAndScoot.Due(1, id, true, false), "counter-battery threat: one salvo is enough");
                Assert.IsFalse(ShootAndScoot.Due(0, id, true, true), "nothing fired yet: nothing to scoot from");
            }
            Assert.Greater(salvos.Count, 1, "guns do not all move on the same salvo");
            var tracker = new CounterBatteryTracker();
            tracker.Impact(new Vector2(10f, 10f), 5.0);
            Assert.IsTrue(tracker.RecentImpactNear(new Vector2(20f, 10f), SimTunables.Ai.FireMissions.ThreatRadius, 6.0, SimTunables.Ai.FireMissions.ImpactMemoryS));
            Assert.IsFalse(tracker.RecentImpactNear(new Vector2(20f, 10f), SimTunables.Ai.FireMissions.ThreatRadius, 30.0, SimTunables.Ai.FireMissions.ImpactMemoryS));
        }

        // ------------------------------------------------------------------------------------------------ 224 pursuit

        [Test]
        public void S224_PursuitLeash_ADefendingSquadReturnsToItsObjectiveWhenTheLeashRunsOut()
        {
            var anchor = new Vector2(0f, 0f);
            var max = SimTunables.Ai.Pursuit.MaxDistance;
            Assert.AreEqual(PursuitVerdict.Continue, PursuitDiscipline.Check(true, 10.0, 5.0, 20f, new Vector2(30f, 0f), anchor, max, 0f, false));
            Assert.AreEqual(PursuitVerdict.Leash, PursuitDiscipline.Check(true, 10.0, 5.0, 20f, new Vector2(max + 10f, 0f), anchor, max, 0f, false));
            Assert.AreEqual(PursuitVerdict.TimeOut, PursuitDiscipline.Check(true, 30.0, 5.0, 20f, new Vector2(30f, 0f), anchor, max, 0f, false));
            Assert.AreEqual(PursuitVerdict.NotMissionRelevant, PursuitDiscipline.Check(true, 10.0, 5.0, 20f, new Vector2(30f, 0f), anchor, max, 0.9f, false));
            Assert.AreEqual(PursuitVerdict.Continue, PursuitDiscipline.Check(true, 10.0, 5.0, 20f, new Vector2(30f, 0f), anchor, max, 0.9f, true),
                "a target threatening the objective is kept under urgency");
            Assert.AreEqual(PursuitVerdict.TargetGone, PursuitDiscipline.Check(false, 10.0, 5.0, 20f, new Vector2(30f, 0f), anchor, max, 0f, false));
            // Spec 206: losses round the chase shrink the leash (bait resistance), never below the floor.
            Assert.AreEqual(60f, PursuitDiscipline.BaitLeash(60f, 0f), 1e-4f);
            Assert.Less(PursuitDiscipline.BaitLeash(60f, 1f), 60f);
            Assert.AreEqual(60f * SimTunables.Ai.Pursuit.BaitLeashMin, PursuitDiscipline.BaitLeash(60f, 10f), 1e-4f);
        }

        [Test]
        public void S146_S147_InterceptLeadsTheTargetAndCutoffOnlyWhenItIsSooner()
        {
            Vector2 self = new(0f, 0f), target = new(100f, 0f), velocity = new(0f, 5f);
            var p = PursuitDiscipline.Intercept(self, 10f, target, velocity, 20f, 0f, out var t);
            Assert.AreEqual(10f * t, Vector2.Distance(self, p), 0.05f, "the intercept point is reached at the same time");
            Assert.Greater(p.Y, 0f, "aimed ahead of the target, not at it");
            PursuitDiscipline.Intercept(self, 10f, target, velocity, 6f, 0f, out var clamped);
            Assert.AreEqual(6f, clamped, 1e-4f, "clamped to the horizon");
            Assert.AreEqual(target, PursuitDiscipline.Intercept(self, 10f, target, velocity, 6f, SimTunables.Ai.Pursuit.AgeFadeS, out _),
                "a long-hidden target is not extrapolated");
            Assert.IsTrue(PursuitDiscipline.CutoffBetter(5f, 8f, 10f));
            Assert.IsFalse(PursuitDiscipline.CutoffBetter(9f, 8f, 10f), "it would get there first");
            Assert.IsFalse(PursuitDiscipline.CutoffBetter(5f, 8f, 4f), "direct pursuit catches it sooner");
        }

        // ------------------------------------------------------------------------------------------------ 207

        [Test]
        public void S207_ObjectiveDeadline_ASlowSquadIsNotSentInVainAFastOneIs()
        {
            Assert.IsFalse(ObjectiveRules.DeadlineUseful(40f, 20f), "slow squad, 20 s left");
            Assert.IsTrue(ObjectiveRules.DeadlineUseful(10f, 20f), "fast squad");
            Assert.IsTrue(ObjectiveRules.DeadlineUseful(21f, 20f), "inside the slack");
            Assert.IsTrue(ObjectiveRules.DeadlineUseful(500f, float.PositiveInfinity), "no deadline");
            // ETA from distance and the slowest member's speed (with the path detour).
            Assert.AreEqual(100f * SimTunables.Ai.AttackSync.Detour / 4f, SyncPlanner.Eta(100f, 4f), 1e-3f);
        }

        // ------------------------------------------------------------------------------------------------ 212

        [Test]
        public void S212_CounterattackOpportunity_OpensOnlyAfterObservedHeavyEnemyLosses()
        {
            var share = SimTunables.Ai.Objectives.CounterLossShare;
            Assert.IsTrue(CounterattackWindow.Opens(6f, 8f, share), "6 of 14 lost");
            Assert.IsFalse(CounterattackWindow.Opens(2f, 10f, share), "a scratch");
            Assert.IsFalse(CounterattackWindow.Opens(0f, 0f, share), "nothing seen lost");
            var memory = new TacticalMemory();
            memory.AddEnemyLoss(new Vector2(10f, 0f), 12f, 3.0);
            Assert.AreEqual(1, memory.EnemyLosses.Count, "only losses the side saw are kept (the event hook checks sight)");
            Assert.AreEqual(0, memory.Deaths.Count, "an enemy loss is no danger mark of ours");
        }

        // ------------------------------------------------------------------------------------------------ 224 sync flank

        [Test]
        public void S224_SynchronizedEta_MainStagesAboutFourSecondsAndContactIsWithinThree()
        {
            var etas = new[] { 8f, 12f };
            var delay = SyncPlanner.ExecuteDelay(etas);
            Assert.AreEqual(12f, delay, 1e-4f);
            Assert.AreEqual(4f, SyncPlanner.StageSeconds(delay, 8f), 1e-4f, "main stages ~4 s");
            Assert.AreEqual(0f, SyncPlanner.StageSeconds(delay, 12f), 1e-4f, "the flank goes at once");
            Assert.LessOrEqual(SyncPlanner.ContactDelta(etas, delay), SimTunables.Ai.AttackSync.GroundToleranceS);
            // Inside the tolerance nobody waits; the contact spread stays within it.
            var near = new[] { 8f, 10f };
            Assert.AreEqual(0f, SyncPlanner.StageSeconds(SyncPlanner.ExecuteDelay(near), 8f), 1e-4f);
            Assert.LessOrEqual(SyncPlanner.ContactDelta(near, SyncPlanner.ExecuteDelay(near)), 3f);
            // Artillery prep lands before ground contact; nobody waits past the cap.
            Assert.GreaterOrEqual(SyncPlanner.ExecuteDelay(new[] { 0.5f }, 0.01f), SimTunables.Ai.AttackSync.ArtilleryPrepLeadS);
            Assert.LessOrEqual(SyncPlanner.ExecuteDelay(new[] { 1f, 90f }), 1f + SimTunables.Ai.AttackSync.MaxStageS + 1e-3f);
        }

        // ------------------------------------------------------------------------------------------------ 224 route diversity

        [Test]
        public void S224_RouteDiversity_TwoEqualSquadsOnTwoEqualCorridorsSplit()
        {
            var book = new RouteBook();
            var mids = new[] { new Vector2(0f, 50f), new Vector2(0f, -50f) };
            var costs = new[] { 1f, 1f };
            var first = RouteDiversity.Choose(costs, mids, book, 1, 0.0);
            book.Book(1, mids[first], 0.0);
            var second = RouteDiversity.Choose(costs, mids, book, 2, 0.0);
            Assert.AreNotEqual(first, second, "occupancy splits them");
            Assert.AreEqual(0, RouteDiversity.Choose(new[] { 1f, 3f }, mids, book, 2, 0.0), "a clearly best route is still taken");
            Assert.AreEqual(first, RouteDiversity.Choose(costs, mids, book, 1, 0.0), "a squad's own booking does not count against it");
            var memory = new TacticalMemory();
            var key = TacticalMemory.RouteKey(new Vector2(100f, 0f), -1);
            memory.Fail(key, 0.0);
            Assert.AreEqual(SimTunables.Ai.Memory.RepeatPlanPenalty, memory.RoutePenalty(key, 0.0), 1e-4f, "a route that just failed costs more");
            Assert.AreEqual(SimTunables.Ai.Memory.RepeatPlanPenalty * 0.5f, memory.RoutePenalty(key, SimTunables.Ai.Memory.RepeatPlanHalfLifeS), 1e-3f, "and fades");
        }

        // ------------------------------------------------------------------------------------------------ 224 reserve

        [Test]
        public void S224_Reserve_PrimaryCollapseReleasesItAnEasySecondaryFightDoesNot()
        {
            var collapse = new ReserveCandidate(3, new Vector2(0f, 0f), 2f, 5f, "primary collapse");
            var easy = new ReserveCandidate(5, new Vector2(50f, 0f), 10f, 2f, "secondary");
            Assert.AreEqual(-1, ReserveLogic.Pick(new[] { easy }), "never into a fight already won");
            Assert.AreEqual(0, ReserveLogic.Pick(new[] { collapse, easy }));
            Assert.AreEqual(1, ReserveLogic.Pick(new[] { easy, collapse }), "by rank, not by list order");
            var hq = new ReserveCandidate(1, new Vector2(0f, -80f), 1f, 3f, "hq");
            Assert.AreEqual(2, ReserveLogic.Pick(new[] { collapse, easy, hq }), "the HQ first");
            Assert.IsTrue(ReserveLogic.Won(5f, 0f), "nothing to fight there");
        }

        // ------------------------------------------------------------------------------------------------ 138-142

        [Test]
        public void S139_PlannedDamage_ASecondShooterSeesTheReservationAndItExpires()
        {
            var board = new PlannedActionBoard();
            EntityId target = new(5), a = new(1), b = new(2);
            board.ReserveDamage(target, a, 0, 60f, 10.0);
            Assert.AreEqual(60f, board.PlannedDamage(target, b, 1.0), 1e-4f);
            Assert.AreEqual(0f, board.PlannedDamage(target, a, 1.0), 1e-4f, "its own reservation does not stop the shooter");
            Assert.IsTrue(PlannedActionBoard.Overkill(60f, 0f, 50f), "60 planned on 50 hp: another target");
            Assert.IsFalse(PlannedActionBoard.Overkill(40f, 0f, 50f));
            Assert.AreEqual(0f, board.PlannedDamage(target, b, 11.0), 1e-4f, "timed out");
            board.ReserveDamage(target, a, 0, 60f, 10.0);
            board.ReserveDamage(new EntityId(6), a, 0, 30f, 10.0);
            Assert.AreEqual(0f, board.PlannedDamage(target, b, 1.0), 1e-4f, "one target per mount: the change releases the old one");
        }

        [Test]
        public void S140_S142_RepairAndSmokeAreNotDoubled()
        {
            var board = new PlannedActionBoard();
            EntityId tank = new(7), e1 = new(1), e2 = new(2);
            board.ReserveRepair(tank, e1, 40f, 10.0);
            var reserved = board.RepairReserved(tank, e2, 1.0);
            Assert.AreEqual(40f, reserved, 1e-4f);
            Assert.IsFalse(PlannedActionBoard.RepairDeficit(30f, reserved), "need covered: no second engineer");
            Assert.IsTrue(PlannedActionBoard.RepairDeficit(100f, reserved), "a deficit left: another may come");
            board.PlanSmoke(new SmokeMission(new Vector2(0f, 0f), 10f, 0.0, 20.0, SmokePurpose.Crossing));
            Assert.IsTrue(board.SmokeCovered(new Vector2(5f, 0f), 1.0), "no second smoke on the same spot");
            Assert.IsFalse(board.SmokeCovered(new Vector2(60f, 0f), 1.0));
            Assert.IsFalse(board.SmokeCovered(new Vector2(5f, 0f), 21.0), "after its end");
            Assert.IsTrue(board.SmokeCovered(new Vector2(5f, 0f), 30.0, new[] { (new Vector2(0f, 0f), 8f) }), "a cloud on the field counts");
        }

        // ------------------------------------------------------------------------------------------------ 125, 149, 151, 171, 172, 199, 211

        [Test]
        public void S125_ConfidenceIsMechanicalAndGatesFreshCommitments()
        {
            Assert.AreEqual(0.5f, TacticalConfidence.NormalizeForceRatio(1f, 1f), 1e-4f);
            Assert.AreEqual(1f, TacticalConfidence.NormalizeForceRatio(3f, 0f), 1e-4f);
            Assert.AreEqual(1f, TacticalConfidence.Compute(1f, 1f, 1f, 1f, 1f, 1f), 1e-4f);
            Assert.AreEqual(0f, TacticalConfidence.Compute(0f, 0f, 0f, 0f, 0f, 0f), 1e-4f);
            Assert.AreEqual("noCommit", TacticalConfidence.Band(0.2f));
            Assert.AreEqual("aggressive", TacticalConfidence.Band(0.8f));
            Assert.IsFalse(TacticalConfidence.MayCommit(0.2f, false));
            Assert.IsTrue(TacticalConfidence.MayCommit(0.2f, true), "an emergency objective still gets committed to");
        }

        [Test]
        public void S149_S199_StancesAndFocusRules()
        {
            Assert.AreEqual(UnitStance.HoldFire, StanceRules.For(DoctrineRole.MainBattle, SquadAction.Hold, true, false), "ambush");
            Assert.AreEqual(UnitStance.ReturnFire, StanceRules.For(DoctrineRole.Recon, SquadAction.Hold, false, false), "recon");
            Assert.AreEqual(UnitStance.Defend, StanceRules.For(DoctrineRole.Support, SquadAction.Attack, false, false), "fragile support");
            Assert.AreEqual(UnitStance.AttackAnything, StanceRules.For(DoctrineRole.MainBattle, SquadAction.Attack, false, false), "assault");
            Assert.IsTrue(StanceRules.ReturnFireAllows(true, 10.0, double.NegativeInfinity));
            Assert.IsTrue(StanceRules.ReturnFireAllows(false, 10.0, 8.0), "just hit");
            Assert.IsFalse(StanceRules.ReturnFireAllows(false, 10.0, 2.0));
            Assert.IsFalse(FocusRules.Strong(false, false, 0.9f, false), "spread fire on an ordinary target");
            Assert.IsTrue(FocusRules.Strong(false, false, 0.2f, false), "near kill");
            Assert.IsTrue(FocusRules.Strong(false, true, 1f, false), "boss part");
        }

        [Test]
        public void S151_PreferredRangeKeepsAMarginInsideTheLimits()
        {
            var catalog = GameContent.LoadCatalog();
            var gun = catalog.Weapons.Values.First(w => w.MinRange > 0f && w.Range > w.MinRange + 10f);
            Assert.Less(RangeBands.PreferredMax(gun), gun.Range);
            Assert.Greater(RangeBands.PreferredMin(gun), gun.MinRange);
            Assert.AreEqual(gun.Range * (1f - SimTunables.Ai.RangeMargin.Artillery), RangeBands.PreferredMax(gun), 1e-3f);
            var direct = catalog.Weapons.Values.First(w => w.MinRange <= 0f && !w.Lofted && !w.Guided && w.Range > 0f);
            Assert.AreEqual(direct.Range * (1f - SimTunables.Ai.RangeMargin.Direct), RangeBands.PreferredMax(direct), 1e-3f);
        }

        [Test]
        public void S171_S172_S211_EconomyOfForceSunkCostAndDepth()
        {
            Assert.AreEqual(8f, ObjectiveRules.SecondaryNeed(10f, 100f), 1e-4f, "enough to delay");
            Assert.AreEqual(100f * SimTunables.Ai.Objectives.EconomyMaxShare, ObjectiveRules.SecondaryNeed(1000f, 100f), 1e-3f, "never half the army");
            var dear = ObjectiveRules.RecoveryCost(45f, 5f, 10f);
            Assert.IsTrue(ObjectiveRules.SunkCostReset(dear, SimTunables.Ai.Objectives.SunkValue), "three tanks lost against twice our strength");
            Assert.IsFalse(ObjectiveRules.SunkCostReset(ObjectiveRules.RecoveryCost(15f, 10f, 10f), SimTunables.Ai.Objectives.SunkValue), "one loss is not a reason");
            var lines = ObjectiveRules.DepthLines(new Vector2(0f, 0f), new Vector2(0f, -100f), 3, 0.3f);
            Assert.AreEqual(3, lines.Length);
            Assert.AreEqual(new Vector2(0f, 0f), lines[0]);
            Assert.AreEqual(-30f, lines[1].Y, 1e-3f);
            Assert.AreEqual(-60f, lines[2].Y, 1e-3f);
        }
    }
}
