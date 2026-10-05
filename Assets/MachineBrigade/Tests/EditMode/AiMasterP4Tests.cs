using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P4 (lane A, DECISIONS "AI MASTER P4 (lane A)"): the advanced-planning rows of Part R / section 224 - the
    /// forecast (frontal bad, flank good: the flank plan wins), forecast / dependency abort, anti-repetition, probe and
    /// conditional-feint utility, boss telegraph escape sectors and pattern learning, utilization - plus the pressure
    /// budget, the deterministic stagger, intent ownership, weakpoint utility, difficulty gating and the air rules. The
    /// rules are tested on the P4 classes the commander, squads and bosses call (deterministic, no world needed). Written by
    /// the lane, not run by it (the lead runs them).
    /// </summary>
    [Category("AIMasterP4")]
    public class AiMasterP4Tests
    {
        [SetUp]
        public void SetUp() => SimTunables.Reset();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        private static ForceEstimate Own() => new ForceEstimate { Hp = 1000f, Strength = 40f, DpsGround = 60f, Reach = 40f, Speed = 6f, Count = 4 };

        private static ForceEstimate Enemy() => new ForceEstimate { Hp = 900f, Strength = 35f, DpsGround = 90f, Reach = 50f, Speed = 1f, Count = 3 };

        // ------------------------------------------------------------------------------------------------ 224 forecast

        [Test]
        public void S224_Forecast_FrontalBadFlankGood_TheFlankPlanWins()
        {
            var own = Own();
            var enemy = Enemy();
            var horizon = SimTunables.Ai.Forecast.Seconds;
            var frontal = CombatForecaster.Forecast(own, enemy, horizon, 40f);
            var flank = CombatForecaster.Forecast(own, enemy, horizon, 40f, SimTunables.Ai.Planning.FlankDpsBonus, SimTunables.Ai.Planning.FlankEnemyUptime);
            Assert.Greater(flank.FriendlyPowerAfter, frontal.FriendlyPowerAfter, "the flank loses less (fewer enemy guns bear)");
            Assert.Less(flank.EnemyPowerAfter, frontal.EnemyPowerAfter, "and kills more (side armour)");
            Assert.Greater(flank.Breakthrough, frontal.Breakthrough);
            var plans = new List<PlanCandidate>
            {
                ShallowPlanner.Score(PlanKind.AttackNow, frontal, own.Strength, enemy.Strength, 0f, 0f, 0f, 0f, 0f, 0f),
                ShallowPlanner.Score(PlanKind.Flank, flank, own.Strength, enemy.Strength, 3f, 0f, 0f, 0f, 0f, 0f, true, -1),
            };
            Assert.AreEqual(1, ShallowPlanner.Pick(plans), "the flank plan wins despite its 3 s detour");
            // Depth 1-2 only, no search: the same inputs give the same forecast.
            var again = CombatForecaster.Forecast(own, enemy, horizon, 40f);
            Assert.AreEqual(frontal.FriendlyPowerAfter, again.FriendlyPowerAfter, 1e-6f);
            // Out of reach the own guns bear later (range uptime), so the same fight from far is worse for the attacker.
            var far = CombatForecaster.Forecast(own, enemy, horizon, 70f);
            Assert.Less(far.EnemyLoss, frontal.EnemyLoss);
        }

        [Test]
        public void S154_ShallowPlans_DifficultyGatesTheCandidatesAndAHoldBeatsASuicide()
        {
            Assert.AreEqual(1, ShallowPlanner.Count(0), "Easy: one forecast plan");
            Assert.AreEqual(2, ShallowPlanner.Count(1), "Normal: two");
            Assert.AreEqual(3, ShallowPlanner.Count(2), "Hard: three");
            Assert.AreEqual(4, ShallowPlanner.Count(3), "Very Hard: all four");
            Assert.AreEqual(PlanKind.AttackNow, ShallowPlanner.Kind(0));
            // An attack that leaves under the hold floor of the own force loses to a valid hold (pre-contact, no emergency).
            var own = new ForceEstimate { Hp = 300f, Strength = 12f, DpsGround = 10f, Reach = 30f, Speed = 5f, Count = 2 };
            var enemy = new ForceEstimate { Hp = 2000f, Strength = 60f, DpsGround = 150f, Reach = 45f, Speed = 1f, Count = 6 };
            var attack = CombatForecaster.Forecast(own, enemy, 6f, 30f);
            Assert.Less(attack.FriendlyPowerAfter, SimTunables.Ai.Planning.HoldPowerFloor);
            var plans = new List<PlanCandidate>
            {
                ShallowPlanner.Score(PlanKind.AttackNow, attack, own.Strength, enemy.Strength, 0f, 0f, 0f, 0f, 0f, 0f),
                ShallowPlanner.Score(PlanKind.SplitHold, CombatForecast.None, own.Strength, enemy.Strength, 12f, 0f, 0f, 0f, 0f, 0f),
            };
            Assert.AreEqual(PlanKind.SplitHold, plans[ShallowPlanner.Pick(plans)].Kind);
            // The hold is a forecast rule, not health: under an emergency objective the caller marks it invalid and the attack goes.
            plans[1] = ShallowPlanner.Score(PlanKind.SplitHold, CombatForecast.None, own.Strength, enemy.Strength, 12f, 0.9f, 0f, 0f, 0f, 0f, false);
            Assert.AreEqual(PlanKind.AttackNow, plans[ShallowPlanner.Pick(plans)].Kind);
        }

        [Test]
        public void S153_Forecast_EnoughStopsBuyingOnlyOnAKnownWeakEnemy()
        {
            var own = new ForceEstimate { Hp = 3000f, Strength = 120f, DpsGround = 300f, Reach = 40f, Speed = 5f, Count = 10 };
            var enemy = new ForceEstimate { Hp = 600f, Strength = 30f, DpsGround = 40f, Reach = 40f, Speed = 5f, Count = 4 };
            var f = CombatForecaster.Forecast(own, enemy, 6f, 0f);
            Assert.IsTrue(CombatForecaster.Enough(own.Strength, enemy.Strength, 4, f));
            Assert.IsFalse(CombatForecaster.Enough(own.Strength, enemy.Strength, 1, f), "too few known enemies: unknown is not weak");
            Assert.IsFalse(CombatForecaster.Enough(50f, enemy.Strength, 4, f), "not twice the known power");
        }

        // ------------------------------------------------------------------------------------------------ 155 / 183 abort

        [Test]
        public void S155_ForecastAbort_AnEnemyEstimateRiseAbortsBeforeContactOnly_NeverAUnitsHealth()
        {
            var made = new PlanDependencies(1, 7, new Vector2(100f, 0f), 10f, true, false);
            var rose = new PlanDependencies(1, 7, new Vector2(104f, 0f), 16f, true, false);
            var broken = PlanDependencies.Broken(made, rose, PlanKind.AttackNow);
            Assert.AreEqual(P4Reasons.DepEnemyRise, broken);
            Assert.AreEqual(P4Reasons.DepEnemyRise, AbortRules.Check(true, broken, false, false, false), "before contact: abort");
            Assert.IsNull(AbortRules.Check(false, broken, false, false, false), "in contact: the package fights on");
            // Small changes never invalidate a plan (spec 183).
            var small = new PlanDependencies(1, 7, new Vector2(110f, 0f), 12f, true, false);
            Assert.IsNull(PlanDependencies.Broken(made, small, PlanKind.AttackNow));
            Assert.AreEqual(P4Reasons.DepCluster, PlanDependencies.Broken(made, new PlanDependencies(1, 7, new Vector2(140f, 0f), 10f, true, false), PlanKind.AttackNow));
            Assert.AreEqual(P4Reasons.DepRoute, PlanDependencies.Broken(made, new PlanDependencies(2, 7, made.ClusterCentre, 10f, true, false), PlanKind.Flank));
            Assert.AreEqual(P4Reasons.DepObjective, PlanDependencies.Broken(made, new PlanDependencies(1, 8, made.ClusterCentre, 10f, true, false), PlanKind.AttackNow));
            var noGuns = new PlanDependencies(1, 7, made.ClusterCentre, 10f, false, false);
            Assert.AreEqual(P4Reasons.DepSupport, PlanDependencies.Broken(made, noGuns, PlanKind.WaitArtillery), "plan B rests on the guns");
            Assert.IsNull(PlanDependencies.Broken(made, noGuns, PlanKind.AttackNow), "plan A does not");
            Assert.AreEqual(P4Reasons.AbortMainLost, AbortRules.Check(true, null, true, false, false));
            Assert.AreEqual(P4Reasons.AbortFlankBlocked, AbortRules.Check(true, null, false, true, false));
            Assert.AreEqual(P4Reasons.AbortSupportFailed, AbortRules.Check(true, null, false, false, true));
            // A damaged unit is not even an input: with every assumption intact nothing aborts.
            Assert.IsNull(AbortRules.Check(true, null, false, false, false));
            Assert.AreNotEqual(made.Hash, rose.Hash, "the versions hash for the log");
        }

        // ------------------------------------------------------------------------------------------------ 158 anti-repetition

        [Test]
        public void S158_AntiRepetition_AFailedPlanLosesTwentyFiveToFiftyPercentAndTheMemoryFades()
        {
            var memory = new RepetitionMemory();
            var target = new Vector2(200f, 50f);
            var key = RepetitionMemory.Key(PlanKind.AttackNow, target);
            Assert.AreEqual(0f, memory.Penalty(key, 0.0), 1e-6f);
            memory.Fail(key, 1f, 10.0);
            Assert.AreEqual(0.5f, memory.Penalty(key, 10.0), 1e-4f, "a bad failure: 50 %");
            Assert.AreEqual(0.25f, memory.Penalty(key, 10.0 + SimTunables.Ai.Planning.RepeatHalfLifeS), 1e-3f, "halved after the half-life");
            var light = new RepetitionMemory();
            light.Fail(key, 0f, 10.0);
            Assert.AreEqual(0.25f, light.Penalty(key, 10.0), 1e-4f, "a light failure: 25 %");
            Assert.AreEqual(0f, memory.Penalty(RepetitionMemory.Key(PlanKind.Flank, target), 10.0), 1e-6f, "only the plan that failed");
            // Equal plans: the one that just failed loses; minutes later it is chosen again (no permanent fear, no randomness).
            var f = new CombatForecast(100f, 300f, 0.8f, 0.4f, 0.6f);
            List<PlanCandidate> Plans(double now) => new()
            {
                ShallowPlanner.Score(PlanKind.AttackNow, f, 40f, 35f, 0f, 0f, 0f, 0f, 0f, memory.Penalty(key, now)),
                ShallowPlanner.Score(PlanKind.Flank, f, 40f, 35f, 1f, 0f, 0f, 0f, 0f, memory.Penalty(RepetitionMemory.Key(PlanKind.Flank, target), now)),
            };
            Assert.AreEqual(PlanKind.Flank, Plans(12.0)[ShallowPlanner.Pick(Plans(12.0))].Kind);
            Assert.AreEqual(PlanKind.AttackNow, Plans(600.0)[ShallowPlanner.Pick(Plans(600.0))].Kind);
            // Anti-churn: a current plan stays unless the new one beats it by the switch margin.
            var close = new List<PlanCandidate>
            {
                ShallowPlanner.Score(PlanKind.AttackNow, f, 40f, 35f, 0f, 0f, 0f, 0f, 0f, 0f),
                ShallowPlanner.Score(PlanKind.Flank, f, 40f, 35f, 0f, 0f, 0f, 0f, 0.5f, 0f),
            };
            Assert.AreEqual(0, ShallowPlanner.Pick(close, 0), "0.5 points better is not enough to switch");
        }

        // ------------------------------------------------------------------------------------------------ 132 probe

        [Test]
        public void S132_ProbeAndExploit_ASmallForceJudgesTheLaneAndNeverSuicides()
        {
            Assert.IsTrue(ProbeRules.ShareFits(12f, 100f), "8-15 % of the power");
            Assert.IsFalse(ProbeRules.ShareFits(5f, 100f));
            Assert.IsFalse(ProbeRules.ShareFits(25f, 100f));
            Assert.AreEqual(ProbeOutcome.Exploit, ProbeRules.Judge(2f, 0f, 10f, 0f, false, true, false), "low resistance: an exploit window");
            Assert.AreEqual(ProbeOutcome.Threat, ProbeRules.Judge(2f, 15f, 10f, 0f, false, true, false), "high anti-tank: a threat (artillery / flank / SEAD)");
            Assert.AreEqual(ProbeOutcome.Threat, ProbeRules.Judge(2f, 0f, 6f, 0.4f, false, false, false), "an ambush that cost a third of the probe");
            Assert.AreEqual(ProbeOutcome.Blocked, ProbeRules.Judge(0f, 0f, 10f, 0f, true, false, false), "no way through: the main army is not sent");
            Assert.AreEqual(ProbeOutcome.Pending, ProbeRules.Judge(0f, 0f, 10f, 0f, false, false, false));
            Assert.AreEqual(ProbeOutcome.Inconclusive, ProbeRules.Judge(20f, 0f, 10f, 0f, false, false, true));
            // The envelope: never closer than its share of the reach to the known enemy.
            var enemy = new Vector2(100f, 0f);
            var goal = ProbeRules.EnvelopeGoal(new Vector2(0f, 0f), enemy, new Vector2(98f, 0f), 40f);
            Assert.GreaterOrEqual(Vector2.Distance(goal, enemy), SimTunables.Ai.Probe.Envelope * 40f - 1e-3f);
            Assert.AreEqual(new Vector2(20f, 0f), ProbeRules.EnvelopeGoal(Vector2.Zero, enemy, new Vector2(20f, 0f), 40f), "far goals stay");
        }

        // ------------------------------------------------------------------------------------------------ 133 feint

        [Test]
        public void S133_ConditionalFeint_NeedsItsOwnUtilityAndOnlyASeenRedeployIsASuccess()
        {
            var weak = FeintRules.Utility(true, 0f, false, false);
            Assert.Less(weak, SimTunables.Ai.Feint.MinUtility, "contesting a point alone is not enough");
            Assert.IsFalse(FeintRules.Allowed(2, false, 0f, weak));
            var good = FeintRules.Utility(true, 0.5f, true, false);
            Assert.GreaterOrEqual(good, SimTunables.Ai.Feint.MinUtility);
            Assert.IsTrue(FeintRules.Allowed(2, false, 0f, good), "Hard");
            Assert.IsTrue(FeintRules.Allowed(3, false, 0f, good), "Very Hard");
            Assert.IsFalse(FeintRules.Allowed(0, true, 0f, good), "never on Easy");
            Assert.IsFalse(FeintRules.Allowed(1, false, 0f, good), "Normal only with a tactic that plays it");
            Assert.IsTrue(FeintRules.Allowed(1, true, 0f, good));
            Assert.IsFalse(FeintRules.Allowed(3, true, 0.9f, good), "an objective emergency beats the feint (226)");
            Assert.IsTrue(FeintRules.Succeeded(10f, 7f, 0f, 3f), "30 % of the seen defenders left and more are seen at the feint");
            Assert.IsFalse(FeintRules.Succeeded(10f, 9f, 0f, 3f), "too few left");
            Assert.IsFalse(FeintRules.Succeeded(10f, 5f, 3f, 3f), "nobody seen arriving at the feint: no hidden reaction read");
            Assert.IsFalse(FeintRules.Succeeded(0f, 0f, 0f, 3f), "nothing seen before: nothing to judge");
        }

        // ------------------------------------------------------------------------------------------------ 180-181, 214 boss telegraph

        [Test]
        public void S181_BossTelegraph_EscapeSectorsSpreadTheSquadAndSkipBlockedOnes()
        {
            var centre = Vector2.Zero;
            const float radius = 10f;
            var members = new List<Vector2> { new(2f, 0f), new(2f, 1f), new(1f, 2f), new(-1f, 1f), new(0f, -2f), new(1f, -1f) };
            var sectors = EscapeSectors.Assign(centre, radius, members, 4, new Vector2(1f, 0f), null, null, out var exits);
            var used = new Dictionary<int, int>();
            for (var i = 0; i < members.Count; i++)
            {
                Assert.GreaterOrEqual(sectors[i], 0);
                used[sectors[i]] = used.TryGetValue(sectors[i], out var n) ? n + 1 : 1;
                Assert.GreaterOrEqual(Vector2.Distance(exits[i], centre), radius + SimTunables.Ai.BossTactics.SectorMargin - 0.01f, "out of the ring");
                for (var j = 0; j < i; j++) Assert.Greater(Vector2.Distance(exits[i], exits[j]), 1f, "never one point for two members");
            }
            Assert.GreaterOrEqual(used.Count, 2, "the squad does not run to one spot");
            foreach (var kv in used) Assert.LessOrEqual(kv.Value, 2, "capacity ceil(6 / 4)");
            // A blocked sector (another ring, the map edge) gets nobody.
            var blocked = EscapeSectors.Assign(centre, radius, members, 4, new Vector2(1f, 0f), p => p.X > 5f, null, out _);
            foreach (var s in blocked) Assert.AreNotEqual(0, s);
            var none = EscapeSectors.Assign(centre, radius, members, 4, new Vector2(1f, 0f), p => true, null, out _);
            foreach (var s in none) Assert.AreEqual(-1, s, "all blocked: the caller falls back to the radial way out");
            // Difficulty changes the quality only: 3 sectors on Easy, 5 on Very Hard.
            Assert.AreEqual(3, DifficultyGate.Sectors(0));
            Assert.AreEqual(5, DifficultyGate.Sectors(3));
        }

        [Test]
        public void S214_PatternLearning_AFollowUpSeenOnceMakesThatSectorCostMoreNextTime()
        {
            var memory = new PatternMemory();
            var sig = PatternMemory.Signature(42, 10f);
            var axis = new Vector2(1f, 0f);
            Assert.AreEqual(0f, memory.Risk(sig, axis, axis), 1e-6f, "nothing learnt before the first attack");
            memory.Seen(sig);
            memory.FollowUp(sig, Vector2.Zero, axis, new Vector2(20f, 0f));
            Assert.AreEqual(1f, memory.Risk(sig, axis, new Vector2(1f, 0f)), 1e-6f, "the follow-up came down ahead");
            Assert.AreEqual(0f, memory.Risk(sig, axis, new Vector2(-1f, 0f)), 1e-6f, "not behind");
            // Same member, same ring: without the pattern it runs ahead; with it, to another sector.
            var member = new List<Vector2> { new(9f, 0.5f) };
            var plain = EscapeSectors.Assign(Vector2.Zero, 10f, member, 4, axis, null, null, out _);
            Assert.AreEqual(0, plain[0]);
            var cost = new float[4];
            for (var k = 0; k < 4; k++)
            {
                var a = k * System.MathF.PI * 0.5f;
                cost[k] = memory.Risk(sig, axis, new Vector2(System.MathF.Cos(a), System.MathF.Sin(a))) * SimTunables.Ai.BossTactics.PatternCost;
            }
            var learnt = EscapeSectors.Assign(Vector2.Zero, 10f, member, 4, axis, null, cost, out _);
            Assert.AreNotEqual(0, learnt[0]);
        }

        // ------------------------------------------------------------------------------------------------ 204, 217

        [Test]
        public void S204_PressureBudget_ANonCriticalCastWaitsBrieflyAndLosesNoDamage()
        {
            Assert.IsTrue(PressureBudget.Defer(2, false, 0f));
            Assert.IsFalse(PressureBudget.Defer(1, false, 0f), "under the budget");
            Assert.IsFalse(PressureBudget.Defer(3, true, 0f), "a scripted salvo never waits (226)");
            Assert.IsFalse(PressureBudget.Defer(3, false, SimTunables.Ai.BossTactics.PressureMaxDelayS), "never longer than the cap");
            Assert.AreEqual(SimTunables.Ai.BossTactics.PressureDelayS, PressureBudget.Wait(0f), 1e-6f);
            Assert.AreEqual(8.5f, PressureBudget.NextCooldown(10f, 1.5f, 3f), 1e-5f, "the wait comes off the next cooldown");
            Assert.AreEqual(3f, PressureBudget.NextCooldown(4f, 2f, 3f), 1e-5f, "never under the minimum");
        }

        [Test]
        public void S217_Stagger_IsDeterministicAndInside150To400Ms()
        {
            var distinct = new HashSet<float>();
            for (var unit = 1; unit <= 20; unit++)
            {
                var d = HumanStagger.Delay(unit, 77);
                Assert.GreaterOrEqual(d, 0.15f - 1e-5f);
                Assert.LessOrEqual(d, 0.4f + 1e-5f);
                Assert.AreEqual(d, HumanStagger.Delay(unit, 77), 0f, "same unit, same event: same delay (no Random)");
                distinct.Add(d);
            }
            Assert.Greater(distinct.Count, 5, "not robot-sync");
            var commit = CommitmentWindows.Seconds(SimTunables.Ai.Commitment.PackageS, 5, 1);
            Assert.GreaterOrEqual(commit, 6f - 1e-5f);
            Assert.LessOrEqual(commit, 12f + 1e-5f);
            Assert.IsTrue(CommitmentWindows.Holds(0.0, 3.0, 6f, false));
            Assert.IsFalse(CommitmentWindows.Holds(0.0, 3.0, 6f, true), "emergency safety breaks a commitment");
        }

        // ------------------------------------------------------------------------------------------------ 224 utilization, Part M

        [Test]
        public void S224_Utilization_AClassThatCannotHitWhatIsInReachBuysLessAfterTwentySeconds()
        {
            var a = new AdaptationTracker();
            for (var t = 0; t <= 40; t++)
            {
                a.SampleUse("ground_gun", false, t);
                a.SampleUse("good_gun", true, t);
                if (t == 15) Assert.AreEqual(1f, a.PurchaseModifier("ground_gun", t), 1e-6f, "not before 20 s of low use");
            }
            var m = a.PurchaseModifier("ground_gun", 40.0);
            Assert.Less(m, 1f, "after 20 s under 15 % the card's modifier falls");
            Assert.GreaterOrEqual(m, SimTunables.Ai.Adaptation.PurchaseFloor - 1e-6f);
            Assert.AreEqual(1f, a.PurchaseModifier("good_gun", 40.0), 1e-6f);
            Assert.AreEqual(1f, a.PurchaseModifier("never_seen", 40.0), 1e-6f);
            // Part M: a repeated bait chase shrinks the leash there only.
            var bait = new Vector2(100f, 100f);
            Assert.AreEqual(1f, a.LeashScale(bait), 1e-6f);
            for (var i = 0; i < SimTunables.Ai.Adaptation.BaitRepeat; i++) a.BaitLoss(bait);
            Assert.AreEqual(SimTunables.Ai.Adaptation.LeashScale, a.LeashScale(bait), 1e-6f);
            Assert.AreEqual(1f, a.LeashScale(new Vector2(400f, 100f)), 1e-6f);
        }

        // ------------------------------------------------------------------------------------------------ ownership, 179, 216, 174-178

        [Test]
        public void P3Leftover_OneOwnerOrdersAGunAtATime()
        {
            var o = new IntentOwnership();
            Assert.IsTrue(o.Claim(7, IntentOwner.Tactical, 2.0, 0.0));
            Assert.IsTrue(o.Claim(7, IntentOwner.FireMission, 10.0, 0.5), "a fire mission takes over the old artillery logic");
            Assert.IsFalse(o.Claim(7, IntentOwner.Tactical, 3.0, 1.0), "the old logic waits while the mission owns the gun");
            Assert.IsTrue(o.HeldByOther(7, IntentOwner.Tactical, 1.0));
            Assert.IsFalse(o.Claim(7, IntentOwner.Scoot, 12.0, 1.0), "equal priority waits for the expiry");
            Assert.IsTrue(o.Claim(7, IntentOwner.Emergency, 3.0, 1.0), "safety beats every plan");
            Assert.AreEqual(IntentOwner.None, o.Owner(7, 20.0), "claims expire");
            Assert.IsTrue(o.Claim(7, IntentOwner.Tactical, 22.0, 20.0));
        }

        [Test]
        public void S179_WeakpointUtility_SilencedDpsUtilityPartsPhaseAndKillProgressCount()
        {
            var plain = WeakpointUtility.Score(0.2f, false, 0f, 1f, 0f);
            Assert.Greater(WeakpointUtility.Score(0.2f, true, 0f, 1f, 0f), plain, "an APS / shield / radar part");
            Assert.Greater(WeakpointUtility.Score(0.2f, false, 1f, 1f, 0f), plain, "it carries the charging big attack");
            Assert.Greater(WeakpointUtility.Score(0.2f, false, 0f, 0.1f, 0f), plain, "nearly broken");
            Assert.Greater(WeakpointUtility.Score(0.6f, false, 0f, 1f, 0f), plain, "more guns silenced");
            Assert.IsTrue(WeakpointUtility.IsUtilityKind("radar_mast"));
            Assert.IsTrue(WeakpointUtility.IsUtilityKind("APS"));
            Assert.IsFalse(WeakpointUtility.IsUtilityKind("hull"));
        }

        [Test]
        public void S216_DifficultyGating_AndAirRules()
        {
            Assert.IsFalse(DifficultyGate.Probe(1));
            Assert.IsTrue(DifficultyGate.Probe(2));
            Assert.IsFalse(DifficultyGate.Adaptation(1));
            Assert.IsTrue(DifficultyGate.Sead(2));
            Assert.IsFalse(DifficultyGate.Sead(1));
            Assert.AreEqual(1, DifficultyGate.Depth(0));
            Assert.AreEqual(2, DifficultyGate.Depth(3));
            // 177: one or two attackers by TTK, never six on one weak target.
            Assert.AreEqual(1, AirRules.Attackers(20f, 10f, 4f, 2));
            Assert.AreEqual(2, AirRules.Attackers(500f, 10f, 4f, 2));
            // 178: a bomber waits for a target worth it, unless urgent; never on a blocked blast or a shut SEAD window.
            Assert.IsFalse(AirRules.BomberGo(1f, false, false, 0f, true, true));
            Assert.IsTrue(AirRules.BomberGo(1f, true, false, 0f, true, true));
            Assert.IsTrue(AirRules.BomberGo(20f, false, false, 0f, true, true));
            Assert.IsFalse(AirRules.BomberGo(20f, false, false, 0f, false, true));
            Assert.IsFalse(AirRules.BomberGo(20f, false, false, 0f, true, false));
            // 176: a fighter past its leash returns; 175: a leg through a SAM bubble is riskier.
            Assert.IsTrue(AirRules.OutsideCap(Vector2.Zero, new Vector2(SimTunables.Ai.AirOps.CapRadius * SimTunables.Ai.AirOps.CapLeash + 1f, 0f)));
            float Threat(Vector2 p) => Vector2.Distance(p, new Vector2(50f, 0f)) < 15f ? 10f : 0f;
            Assert.Greater(AirRules.LegRisk(Threat, Vector2.Zero, new Vector2(100f, 0f), 6), AirRules.LegRisk(Threat, Vector2.Zero, new Vector2(0f, 100f), 6));
        }
    }
}
