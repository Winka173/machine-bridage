using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Movement;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P5 (lane A, DECISIONS "AI MASTER P5 (lane A)"): Part R R8 (the AI Health Monitor detects an injected stalled
    /// squad, triggers a valid re-evaluation and logs the cause), Part L (ammo / reload-aware tactics), Part N (tower
    /// coordination), Part O (one registry: every lane's codes registered, a battle's log consistent), Part P (deterministic
    /// staggering) and a determinism check across the lanes. Rule rows run on the P5 classes without a world; the world rows run
    /// a small AI-against-AI Conquest. Written by the lane, not run by it (the lead runs category AIMasterP5).
    /// </summary>
    [Category("AIMasterP5")]
    public class AiMasterP5Tests
    {
        private const float Step = 0.05f;

        [SetUp]
        public void SetUp() => SimTunables.Reset();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        // ------------------------------------------------------------------------------------------------ worlds

        private static readonly string[] Roster = { "main_battle_tank", "ifv", "armored_car", "tank_destroyer", "main_battle_tank", "light_tank" };

        /// <summary>A Conquest battle on Ashfield with both sides' layered AI and <paramref name="perSide"/> units each (no buying).</summary>
        internal static (SimWorld world, ConquestMode mode, ConquestAi a, ConquestAi b) Conquest(int seed, int perSide, IReadOnlyList<string> roster = null)
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: seed);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles,
                PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles,
                EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, seed + 1) { AutoDeploy = false, Layered = true };
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, seed + 2) { AutoDeploy = false, Layered = true };
            Fill(world, 0, perSide, roster ?? Roster);
            Fill(world, 1, perSide, roster ?? Roster);
            return (world, mode, a, b);
        }

        /// <summary>Tops a side up to <paramref name="count"/> ground units round its rally (deterministic spots).</summary>
        internal static void Fill(SimWorld world, int team, int count, IReadOnlyList<string> roster)
        {
            world.TryGetRally(team, out var at);
            var alive = world.VehicleList.Count(v => v.IsAlive && v.Team == team && !v.Def.Static);
            for (var i = alive; i < count; i++)
            {
                var angle = i * 2.39996f;
                world.SpawnVehicle(roster[i % roster.Count], team, world.ClampToMap(at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (5f + i % 7 * 2.5f)), 0f);
            }
        }

        internal static void Run(SimWorld world, ConquestMode mode, ConquestAi a, ConquestAi b, float seconds)
        {
            for (var t = 0f; t < seconds && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                a.Tick(world, Step);
                b.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
        }

        // ------------------------------------------------------------------------------------------------ R8 health monitor

        [Test]
        public void R8_HealthRules_AStalledSquadIsDetectedOnceAndNotSpammed()
        {
            var st = new SquadHealthState();
            var s = new SquadSample { Team = 1, Squad = 7, Members = 5, InContact = true, LastFireAt = double.NegativeInfinity };
            // Contact starts the clock; under squadNoDamageS nothing is wrong.
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(s, st, 10.0));
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(s, st, 10.0 + SimTunables.Ai.Health.SquadNoDamageS - 1.0));
            var h = HealthRules.Evaluate(s, st, 10.0 + SimTunables.Ai.Health.SquadNoDamageS + 0.5);
            Assert.AreEqual(SquadHealth.NoDamage, h & SquadHealth.NoDamage, "in contact and silent past 10-20 s: stalled");
            Assert.IsTrue(HealthRules.RecoveryDue(h, st, 30.0));
            st.RecoveredAt = 30.0;
            Assert.IsFalse(HealthRules.RecoveryDue(h, st, 30.0 + SimTunables.Ai.Health.RecoveryCooldownS - 1.0), "no command spam (spec 185)");
            Assert.IsTrue(HealthRules.RecoveryDue(h, st, 30.0 + SimTunables.Ai.Health.RecoveryCooldownS));
            // A shot resets the clock; holding / dodging is legitimate standing.
            s.LastFireAt = 40.0;
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(s, st, 41.0) & SquadHealth.NoDamage);
            var hold = s;
            hold.Holding = true;
            hold.LastFireAt = double.NegativeInfinity;
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(hold, new SquadHealthState(), 500.0));
            // Out of contact a squad that never closes on its objective is a stalled assignment, one that progresses is not.
            var go = new SquadHealthState();
            var walk = new SquadSample { Team = 1, Squad = 8, Members = 4, HasObjective = true, ObjectiveDistance = 200f };
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(walk, go, 0.0));
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(walk, go, SimTunables.Ai.Health.StallS - 1.0));
            Assert.AreEqual(SquadHealth.StalledObjective, HealthRules.Evaluate(walk, go, SimTunables.Ai.Health.StallS + 0.5));
            walk.ObjectiveDistance = 200f - SimTunables.Ai.Health.ProgressM - 1f;
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(walk, go, SimTunables.Ai.Health.StallS + 1.0), "progress resets the stall clock");
            walk.ObjectiveDistance = SimTunables.Ai.Health.ArriveRadius - 1f;
            Assert.AreEqual(SquadHealth.Ok, HealthRules.Evaluate(walk, go, 999.0), "arrived");
        }

        [Test]
        public void R8_HealthRules_SystemThresholds()
        {
            Assert.IsFalse(HealthRules.IdleTrips(0, 40));
            Assert.IsTrue(HealthRules.IdleTrips((int)MathF.Ceiling(40 * SimTunables.Ai.Health.IdleTripShare), 40));
            Assert.IsFalse(HealthRules.BlockedTrips(SimTunables.Ai.Health.BlockedMinUnits - 1, 4), "too few to count");
            Assert.IsTrue(HealthRules.BlockedTrips(10, 30));
            Assert.IsFalse(HealthRules.BlockedTrips(5, 40));
        }

        /// <summary>
        /// Part R R8 in a battle: an artificial stalled squad (in contact, never firing) injected into a real AI side. The monitor
        /// detects it, triggers the valid re-evaluation (idle reassessment taken by the squad, goal re-issued, anchors refreshed),
        /// logs WATCHDOG_SQUAD_ZERO_UTILIZATION for that squad, and moves, heals or spawns nothing.
        /// </summary>
        [Test]
        public void R8_InjectedStalledSquad_IsDetectedReEvaluatedAndLogged()
        {
            var (world, mode, a, b) = Conquest(51, 8);
            Run(world, mode, a, b, 5f);
            Assert.IsTrue(world.AiCommanders.ContainsKey(1), "the layered AI made its commander");
            var squad = world.AiCommanders[1].Squads.Squads.FirstOrDefault(s => s.Members.Count > 0);
            Assert.IsNotNull(squad, "squads formed");
            world.Health.Inject(1, squad.Id, new SquadSample
            {
                Team = 1, Squad = squad.Id, Members = squad.Members.Count, InContact = true, LastFireAt = double.NegativeInfinity,
            });
            var before = world.Health.Counters.SquadReevaluations;
            var units = world.VehicleList.Count(v => v.IsAlive);
            Run(world, mode, a, b, SimTunables.Ai.Health.SquadNoDamageS + 3f);
            Assert.Greater(world.Health.Counters.SquadReevaluations, before, "detected and recovered");
            Assert.AreEqual(SquadHealth.NoDamage, world.Health.StateOf(1, squad.Id).Last & SquadHealth.NoDamage);
            Assert.IsTrue(world.AiLog.Entries.Any(e => e.Team == 1 && e.Layer == AiLayer.Squad && e.Subject == squad.Id &&
                                                        e.Text.StartsWith(P5Reasons.SquadZeroUtilization)), "the cause is logged");
            Assert.IsFalse(squad.HealthReassess, "the squad took the request as an idle reassessment on its next think");
            Assert.LessOrEqual(world.VehicleList.Count(v => v.IsAlive), units, "the monitor spawns nothing");
            // One recovery per cooldown (no spam): at most one more within the next cooldown.
            var after = world.Health.Counters.SquadReevaluations;
            Run(world, mode, a, b, SimTunables.Ai.Health.RecoveryCooldownS * 0.5f);
            Assert.LessOrEqual(world.Health.Counters.SquadReevaluations - after, world.AiCommanders[1].Squads.Squads.Count, "cooldown per squad");
            world.Health.ClearInjected();
        }

        [Test]
        public void R8_TheMonitorCountsEveryPartKMetric()
        {
            var (world, mode, a, b) = Conquest(52, 6);
            Run(world, mode, a, b, 8f);
            var c = world.Health.Counters;
            Assert.Greater(c.Passes, 5, "1 Hz passes");
            Assert.AreEqual(0, c.NoMapInfluencePurchases, "rejected before scoring (P0-B)");
            Assert.AreEqual(world.Traffic.Stats.SevereUnstuck, c.SevereUnstuckEvents);
            Assert.AreEqual(world.CombatWatch.Anomalies, c.CombatAnomalies);
            Assert.AreEqual(0, c.NavalReverseAttempts, "no ships here");
            Assert.GreaterOrEqual(c.OrdersPerUnitPerMinute, 0f);
            Assert.GreaterOrEqual(c.BlockedRatio, 0f);
        }

        // ------------------------------------------------------------------------------------------------ Part L ammo / reload

        private static MagazineReading Mag(float fraction, bool reloading, float left, float full, bool onMove) =>
            new MagazineReading(true, fraction, reloading, left, full, onMove);

        [Test]
        public void L1_AnEmptyMeaningfulMagazineDoesNotChargeUnlessTheObjectiveIsAnEmergency()
        {
            var empty = Mag(0f, true, 8f, 12f, false);
            Assert.IsFalse(AmmoTactics.MayCharge(empty, 0.2f, false));
            Assert.IsTrue(AmmoTactics.MayCharge(empty, SimTunables.Ai.Ammo.EmergencyUrgency, false), "objective emergency");
            Assert.IsTrue(AmmoTactics.MayCharge(empty, 0f, true), "overwhelmed / dodging");
            Assert.IsFalse(AmmoTactics.MayCharge(Mag(0.1f, false, 0f, 12f, false), 0f, false), "near empty");
            Assert.IsTrue(AmmoTactics.MayCharge(Mag(0.8f, false, 0f, 12f, false), 0f, false), "full enough");
            Assert.IsTrue(AmmoTactics.MayCharge(Mag(0f, true, 0.5f, 0.8f, false), 0f, false), "a short reload is not meaningful");
            Assert.IsTrue(AmmoTactics.MayCharge(MagazineReading.Unlimited, 0f, false));
            // In a squad advance: an in-place reload holds the unit (it only reloads standing still) and it resumes once loaded.
            Assert.IsTrue(AmmoTactics.HoldBack(empty, true, false, 0f, false));
            Assert.IsFalse(AmmoTactics.HoldBack(empty, false, false, 0f, false), "not advancing: nothing to hold");
            Assert.IsFalse(AmmoTactics.Resume(empty, 0f, false));
            Assert.IsTrue(AmmoTactics.Resume(Mag(1f, false, 0f, 12f, false), 0f, false), "reloaded");
            Assert.IsTrue(AmmoTactics.Resume(empty, 0.9f, false), "emergency");
            // Near empty but not yet reloading is not held (it reloads only once empty: holding it would idle it).
            Assert.IsFalse(AmmoTactics.HoldBack(Mag(0.1f, false, 0f, 12f, false), true, false, 0f, false));
        }

        [Test]
        public void L2_AClipReloadIsARepositionWindow_AnInPlaceReloadIsNot()
        {
            Assert.IsTrue(AmmoTactics.RepositionWindow(Mag(0f, true, SimTunables.Ai.Ammo.RepositionMinReloadS + 1f, 6f, true)));
            Assert.IsFalse(AmmoTactics.RepositionWindow(Mag(0f, true, SimTunables.Ai.Ammo.RepositionMinReloadS + 1f, 6f, false)),
                "moving would pause an in-place reload");
            Assert.IsFalse(AmmoTactics.RepositionWindow(Mag(0f, true, 1f, 6f, true)), "too short");
            // A line unit with a clip is not held: its reload runs on the move.
            Assert.IsFalse(AmmoTactics.HoldBack(Mag(0f, true, 5f, 6f, true), true, false, 0f, false));
        }

        [Test]
        public void L3_ArtilleryScootsInsideAReloadThatRunsOnTheMove()
        {
            var window = Mag(0f, true, SimTunables.Ai.Ammo.ScootMinReloadS + 2f, 20f, true);
            Assert.IsTrue(AmmoTactics.ScootDuringReload(window, 1));
            Assert.IsFalse(AmmoTactics.ScootDuringReload(window, 0), "nothing fired yet");
            Assert.IsFalse(AmmoTactics.ScootDuringReload(Mag(0f, true, 10f, 20f, false), 1), "an in-place reload would pause");
            Assert.IsFalse(AmmoTactics.ScootDuringReload(Mag(0f, true, 1f, 20f, true), 1), "too little left");
        }

        [Test]
        public void L4_SupportWeaponsHoldWhileTheyCannotFire()
        {
            var clip = Mag(0f, true, 5f, 6f, true);
            Assert.IsFalse(AmmoTactics.HoldBack(clip, true, false, 0f, false), "a line unit moves on");
            Assert.IsTrue(AmmoTactics.HoldBack(clip, true, true, 0f, false), "a support weapon does not expose itself while it cannot fire");
            Assert.IsFalse(AmmoTactics.HoldBack(clip, true, true, 0f, true), "unless an emergency");
        }

        [Test]
        public void L5_AReloadingMountKeepsItsValidTarget_NoChurn()
        {
            var empty = Mag(0f, true, 8f, 12f, false);
            Assert.IsTrue(AmmoTactics.KeepTarget(empty, true));
            Assert.IsFalse(AmmoTactics.KeepTarget(empty, false), "an invalid target is dropped as before");
            Assert.IsFalse(AmmoTactics.KeepTarget(Mag(0.5f, false, 0f, 12f, false), true), "not reloading: normal retargeting");
            SimTunables.Ai.Ammo.KeepTargetWhileReloading = false;
            Assert.IsFalse(AmmoTactics.KeepTarget(empty, true), "switch");
        }

        [Test]
        public void L_ReadingAVehicle_AnEmptyMagazineIsReloading()
        {
            var catalog = GameContent.LoadCatalog();
            var def = catalog.Vehicles.Values.OrderBy(d => d.Id, StringComparer.Ordinal)
                .FirstOrDefault(d => !d.Static && !d.Flying && d.Card && d.Mounts.Count > 0 && d.Weapon.Ammo > 0);
            Assert.IsNotNull(def, "a ground card with a magazine");
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            world.TryGetRally(0, out var at);
            var v = world.SpawnVehicle(def.Id, 0, at, 0f);
            var full = AmmoTactics.Read(world, v);
            Assert.IsTrue(full.Limited);
            Assert.IsFalse(full.Reloading);
            Assert.AreEqual(1f, full.Fraction, 1e-4f);
            v.Weapons[0].Ammo = 0;
            var dry = AmmoTactics.Read(world, v);
            Assert.IsTrue(dry.Reloading);
            Assert.AreEqual(0f, dry.Fraction, 1e-4f);
            Assert.Greater(dry.ReloadLeft, 0f);
        }

        // ------------------------------------------------------------------------------------------------ Part N towers

        private static TowerTargetFacts Facts(bool flying = false, bool zone = false, bool heavy = false, bool arty = false, bool critical = false,
            float others = 0f, float hp = 100f, bool mine = false) => new TowerTargetFacts(flying, zone, heavy, arty, critical, others, hp, mine);

        [Test]
        public void N1_TowersAvoidOverkillOnOneWeakUnit()
        {
            Assert.IsTrue(TowerCoordination.Overkill(Facts(others: 120f, hp: 100f)), "two towers' shots already kill it");
            Assert.Less(TowerCoordination.Worth(TowerKind.AntiTank, Facts(others: 120f, hp: 100f)), 1f);
            Assert.IsFalse(TowerCoordination.Overkill(Facts(others: 120f, hp: 100f, mine: true)), "the tower already on it finishes it");
            Assert.IsFalse(TowerCoordination.Overkill(Facts(others: 60f, hp: 100f)), "not enough yet: focus is fine");
            Assert.IsFalse(TowerCoordination.Overkill(Facts(others: 500f, hp: 100f, critical: true)), "a critical threat is never spread off");
        }

        [Test]
        public void N2_SamTowersFirstOnAircraftThreateningTheProtectedZone()
        {
            var threat = TowerCoordination.Worth(TowerKind.AntiAir, Facts(flying: true, zone: true));
            var passing = TowerCoordination.Worth(TowerKind.AntiAir, Facts(flying: true));
            Assert.Greater(threat, passing);
            Assert.AreEqual(SimTunables.Ai.Towers.AirThreatWorth, threat, 1e-4f);
            Assert.AreEqual(1f, TowerCoordination.Worth(TowerKind.AntiTank, Facts(flying: true, zone: true)), 1e-4f, "only AA towers");
        }

        [Test]
        public void N3_AtTowersValueHeavyTargets_N4_ArtilleryTowersValueEnemyArtillery()
        {
            Assert.Greater(TowerCoordination.Worth(TowerKind.AntiTank, Facts(heavy: true)), TowerCoordination.Worth(TowerKind.AntiTank, Facts()));
            Assert.Greater(TowerCoordination.Worth(TowerKind.FireSupport, Facts(arty: true)), TowerCoordination.Worth(TowerKind.FireSupport, Facts()));
            Assert.AreEqual(1f, TowerCoordination.Worth(TowerKind.AntiAir, Facts(heavy: true, arty: true)), 1e-4f);
        }

        [Test]
        public void N5_ACriticalObjectiveThreatOverridesTheTowerMode()
        {
            // AirFirst / ArtilleryFirst give x3 (prompt 28 E.1): a ground unit at the HQ must still win over a passing aircraft.
            const float modeOnAircraft = 3f;
            var critical = TowerCoordination.Worth(TowerKind.AntiAir, Facts(critical: true));
            var aircraft = modeOnAircraft * TowerCoordination.Worth(TowerKind.AntiAir, Facts(flying: true));
            Assert.Greater(critical, aircraft);
            SimTunables.Ai.Towers.Enabled = false;
            Assert.AreEqual(1f, TowerCoordination.Worth(TowerKind.AntiAir, Facts(critical: true)), 1e-4f, "switch");
        }

        // ------------------------------------------------------------------------------------------------ Part O registry

        [Test]
        public void O_EveryLanesCodeIsRegistered()
        {
            var classes = new[] { typeof(CombatReasons), typeof(P2Reasons), typeof(P3Reasons), typeof(P4Reasons), typeof(P5Reasons) };
            var missing = new List<string>();
            foreach (var t in classes)
                foreach (var f in t.GetFields(BindingFlags.Public | BindingFlags.Static).Where(f => f.IsLiteral && f.FieldType == typeof(string)))
                {
                    var code = (string)f.GetRawConstantValue();
                    if (code.EndsWith("_")) continue; // a prefix (P4Reasons.AbortPrefix)
                    if (!ReasonCodes.IsRegistered(code)) missing.Add($"{t.Name}.{f.Name}={code}");
                }
            foreach (TargetReject r in Enum.GetValues(typeof(TargetReject)))
                if (!ReasonCodes.IsRegistered(CombatReasons.Code(r))) missing.Add(CombatReasons.Code(r));
            foreach (CombatIdleReason r in Enum.GetValues(typeof(CombatIdleReason)))
                if (!ReasonCodes.IsRegistered(CombatReasons.Code(r))) missing.Add(CombatReasons.Code(r));
            foreach (JamStage s in Enum.GetValues(typeof(JamStage)))
                if (!ReasonCodes.IsRegistered(JamTracker.Code(s))) missing.Add(JamTracker.Code(s));
            foreach (HullReason h in Enum.GetValues(typeof(HullReason)))
            {
                if (!ReasonCodes.IsRegistered(ReasonCodes.HullCode(h, true))) missing.Add(ReasonCodes.HullCode(h, true));
                if (!ReasonCodes.IsRegistered(ReasonCodes.HullCode(h, false))) missing.Add(ReasonCodes.HullCode(h, false));
            }
            CollectionAssert.IsEmpty(missing, "unregistered codes");
            foreach (var example in ReasonCodes.SpecExamples) Assert.IsTrue(ReasonCodes.IsRegistered(example), example);
        }

        [Test]
        public void O_TheRegistryIsConsistent()
        {
            var codes = ReasonCodes.All.Select(r => r.Code).ToList();
            CollectionAssert.AllItemsAreUnique(codes, "one entry a code");
            var namespaces = new HashSet<string>(ReasonCodes.Namespaces.Concat(ReasonCodes.ExtraNamespaces));
            foreach (var r in ReasonCodes.All)
            {
                Assert.IsTrue(namespaces.Contains(r.Namespace), $"{r.Code}: namespace {r.Namespace}");
                Assert.IsTrue(ReasonCodes.LooksLikeCode(r.Code), r.Code);
                Assert.IsNotEmpty(r.Meaning, r.Code);
            }
            foreach (var ns in ReasonCodes.Namespaces)
                Assert.IsTrue(ReasonCodes.All.Any(r => r.Namespace == ns), $"Part O namespace {ns} has codes");
            Assert.AreEqual("REJECT", ReasonCodes.FirstWord("REJECT main_battle_tank reason=no-map-influence"));
            Assert.IsTrue(ReasonCodes.TryGet("BUY", out var buy) && buy.Code == "PURCHASE_BUY", "section 94 verbs are aliases");
        }

        [Test]
        public void O_ABattlesLogHasOnlyRegisteredCodes()
        {
            var (world, mode, a, b) = Conquest(53, 10);
            Run(world, mode, a, b, 45f);
            Assert.Greater(world.AiLog.Count, 0);
            CollectionAssert.IsEmpty(ReasonCodes.Unregistered(world.AiLog), "every code written is in ReasonCodes.All");
        }

        // ------------------------------------------------------------------------------------------------ Part P / determinism

        [Test]
        public void P_SquadBucketsSpreadTheSquadsEvenlyAndDeterministically()
        {
            const int buckets = 2;
            for (long tick = 0; tick < 8; tick++)
            {
                var due = Enumerable.Range(1, 20).Count(id => AiCadence.Due(id, tick, buckets));
                Assert.AreEqual(10, due, "half the squads each layer tick");
            }
            for (var id = 1; id <= 20; id++)
            {
                var hits = Enumerable.Range(0, 8).Count(t => AiCadence.Due(id, t, buckets));
                Assert.AreEqual(4, hits, "each squad every other tick: 2 Hz at the 4 Hz layer");
                Assert.AreEqual(AiCadence.Due(id, 5, buckets), AiCadence.Due(id, 5, buckets));
            }
            Assert.IsTrue(Enumerable.Range(0, 5).All(t => AiCadence.Due(3, t, 1)), "one bucket: every tick (the old cadence)");
            Assert.AreEqual(2f, AiCadence.RateHz(4f, 2), 1e-4f);
        }

        [Test]
        public void P_TheSpatialIndexCountsTheSameAsAScan()
        {
            var (world, mode, a, b) = Conquest(54, 12);
            Run(world, mode, a, b, 2f);
            foreach (var v in world.VehicleList.Where(x => x.IsAlive))
                foreach (var r in new[] { 8f, 15f })
                {
                    var scan = world.VehicleList.Count(o => o != v && o.IsAlive && o.Team == v.Team && o.Flying == v.Flying &&
                                                            Vector2.DistanceSquared(o.Position, v.Position) <= r * r);
                    Assert.AreEqual(scan, world.Spatial.CountSameSide(v, r), $"{v.Def.Id} r={r}");
                }
        }

        [Test]
        public void P_PerfCountersStayOffByDefaultAndCountWhenOn()
        {
            var (world, mode, a, b) = Conquest(55, 6);
            Run(world, mode, a, b, 1f);
            Assert.AreEqual(0, world.AiPerf.Steps, "off by default");
            world.AiPerf.Enabled = true;
            Run(world, mode, a, b, 3f);
            Assert.Greater(world.AiPerf.Steps, 0);
            Assert.Greater(world.AiPerf.Calls(AiPerfSection.Steering), 0);
            Assert.Greater(world.AiPerf.Calls(AiPerfSection.Squad), 0);
            Assert.Greater(world.AiPerf.Calls(AiPerfSection.Commander), 0);
            Assert.Greater(world.AiPerf.Calls(AiPerfSection.HealthMonitor), 0);
            StringAssert.Contains("Steering", world.AiPerf.Report());
        }

        /// <summary>Tick / determinism review across the lanes: the same seed gives the same decisions and the same battle.</summary>
        [Test]
        public void Determinism_TheSameSeedGivesTheSameDecisionLogAndBattle()
        {
            string Play()
            {
                var (world, mode, a, b) = Conquest(56, 10);
                Run(world, mode, a, b, 40f);
                var log = string.Join("\n", world.AiLog.Entries.Select(e => e.ToString()));
                var state = string.Join(";", world.VehicleList.Select(v => $"{v.Id.Value}:{v.Position.X:0.000},{v.Position.Y:0.000},{v.Hp:0.0}"));
                return log + "\n#\n" + state;
            }
            var first = Play();
            var second = Play();
            Assert.AreEqual(first.Length, second.Length);
            Assert.AreEqual(first, second, "deterministic across every AI lane");
        }
    }
}
