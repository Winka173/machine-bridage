#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Movement;
using Tun = MachineBrigade.Sim.Content.SimTunables.Ai;

namespace MachineBrigade.Sim.AI
{
    /// <summary>AI MASTER P5 Part K: what a squad looks like to the health monitor (observed state only; the tests inject one).</summary>
    public struct SquadSample
    {
        public int Team;
        public int Squad;
        public int Members;

        /// <summary>A known enemy within the squad's reach plus <c>contactMargin</c> of its centre.</summary>
        public bool InContact;

        /// <summary>The latest shot of any member (negative infinity: none yet).</summary>
        public double LastFireAt;

        /// <summary>The squad's objective, if its task has one, and its distance from the centre.</summary>
        public bool HasObjective;
        public float ObjectiveDistance;

        /// <summary>A hold task, a dodge, or the defending stance: standing still without shooting is legitimate.</summary>
        public bool Holding;
    }

    /// <summary>Part K: what the monitor found wrong with a squad.</summary>
    [Flags]
    public enum SquadHealth : byte
    {
        Ok = 0,
        /// <summary>In contact, no member fired for <c>squadNoDamageS</c> (K1 "squad no useful damage for 10-20 s").</summary>
        NoDamage = 1,
        /// <summary>An objective, not in contact, not closer by <c>progressM</c> for <c>stallS</c> (stalledObjectiveAssignments).</summary>
        StalledObjective = 2,
    }

    /// <summary>The monitor's memory of one squad (contact start, progress, last recovery).</summary>
    public sealed class SquadHealthState
    {
        public double ContactSince = double.NaN;
        public float BestDistance = float.PositiveInfinity;
        public double ProgressAt = double.NaN;
        public double RecoveredAt = double.NegativeInfinity;
        public SquadHealth Last;
    }

    /// <summary>The Part K counters (the lead's runs and the Part V report read them).</summary>
    public sealed class HealthCounters
    {
        public int ArmedIdleWithoutReason, SquadsNoDamage, BlockedUnits, SevereUnstuckEvents, NoMapInfluencePurchases;
        public float OrdersPerUnitPerMinute, TargetSwitchesPerMinute, SquadActionSwitchesPerMinute, BlockedRatio;
        public int LowUtilizationUnitClasses, StalledObjectiveAssignments, CombatAnomalies, DeadlockCycles, NavalReverseAttempts;

        /// <summary>Recoveries the monitor triggered, by kind (squad re-evaluations, audits, traffic escalations, churn damps).</summary>
        public int SquadReevaluations, IdleAudits, TrafficEscalations, ChurnDamps, NavalReverseErrors;

        /// <summary>Part L / N effects (counted, not logged per shot).</summary>
        public int ReloadHolds, ReloadResumes, TargetsKeptReloading, ScootsDuringReload, TowerOverkillAvoided, TowerCriticalOverrides;

        /// <summary>Monitor passes so far.</summary>
        public int Passes;
    }

    /// <summary>
    /// AI MASTER P5 Part K: the pure rules of the health monitor (the tests drive them with injected samples, R8).
    /// </summary>
    public static class HealthRules
    {
        /// <summary>Updates <paramref name="st"/> with one sample and returns what is wrong now.</summary>
        public static SquadHealth Evaluate(in SquadSample s, SquadHealthState st, double now)
        {
            var result = SquadHealth.Ok;
            if (s.Members <= 0)
            {
                st.ContactSince = double.NaN;
                st.ProgressAt = double.NaN;
                return st.Last = result;
            }
            // No useful damage in contact (the clock starts at contact or at the last shot, whichever is later).
            if (s.InContact && !s.Holding)
            {
                if (double.IsNaN(st.ContactSince)) st.ContactSince = now;
                var since = Math.Max(st.ContactSince, s.LastFireAt);
                if (now - since >= Tun.Health.SquadNoDamageS) result |= SquadHealth.NoDamage;
            }
            else st.ContactSince = double.NaN;
            // Objective progress (only while not in contact: a fight is not a stall).
            if (s.HasObjective && !s.InContact && !s.Holding && s.ObjectiveDistance > Tun.Health.ArriveRadius)
            {
                if (double.IsNaN(st.ProgressAt) || s.ObjectiveDistance <= st.BestDistance - Tun.Health.ProgressM)
                {
                    st.ProgressAt = now;
                    st.BestDistance = s.ObjectiveDistance;
                }
                else if (now - st.ProgressAt >= Tun.Health.StallS) result |= SquadHealth.StalledObjective;
            }
            else
            {
                st.ProgressAt = double.NaN;
                st.BestDistance = float.PositiveInfinity;
            }
            return st.Last = result;
        }

        /// <summary>K1: a recovery is due (something wrong, and the squad's cooldown over: no command spam, spec 185).</summary>
        public static bool RecoveryDue(SquadHealth h, SquadHealthState st, double now) =>
            h != SquadHealth.Ok && now - st.RecoveredAt >= Tun.Health.RecoveryCooldownS;

        /// <summary>K1 too many idle armed units: the share of armed AI units idle without a reason.</summary>
        public static bool IdleTrips(int idleWithoutReason, int armed) =>
            idleWithoutReason > 0 && armed > 0 && idleWithoutReason >= Math.Max(1f, armed * Tun.Health.IdleTripShare);

        /// <summary>K1 high blocked-unit ratio.</summary>
        public static bool BlockedTrips(int blocked, int moving) =>
            blocked >= Tun.Health.BlockedMinUnits && moving > 0 && blocked >= moving * Tun.Health.BlockedTripShare;
    }

    /// <summary>
    /// AI MASTER P5 Part K: the AI Health Monitor, one per battle (<see cref="SimWorld.Health"/>), above the unit watchdogs
    /// (CombatActivityWatchdog, the jam stages, the boss brains). Once a second (half a second after the commanders) it reads the
    /// counters of every lane, judges the AI sides' squads and, when a threshold trips, triggers only valid re-evaluations through
    /// the existing paths (a squad's idle reassessment, a re-issued goal, a fresh fire-support anchor, a forced retarget, a longer
    /// commitment), and logs the cause (WATCHDOG_* / NAVAL_REVERSE_FORBIDDEN). It never moves, heals, reveals or spawns anything.
    /// Deterministic: teams in order, squads in list order, the sim clock; its readings never feed a score.
    /// </summary>
    public sealed class AiHealthMonitor
    {
        private readonly SimWorld _world;
        private readonly Dictionary<(int team, int squad), SquadHealthState> _squads = new();
        private readonly Dictionary<(int team, int squad), double> _damped = new();
        private readonly int[] _idleByReason = new int[Enum.GetValues(typeof(CombatIdleReason)).Length];
        private readonly HashSet<int> _anchorRefresh = new();
        private double _next = global::MachineBrigade.Sim.Content.SimTunables.Ai.AiHealthMonitor.Next;
        private int _lastUnexplained, _lastNavalReverse, _lastLowClasses;
        private (int a, int s, int t) _lastChurn;
        private double _lastChurnAt = double.NaN;
        private readonly long[] _ordersAt = new long[3];
        private double _ordersSince = double.NaN;

        internal AiHealthMonitor(SimWorld world) => _world = world;

        public HealthCounters Counters { get; } = new();

        /// <summary>The monitor's state of a squad (null before its first look).</summary>
        public SquadHealthState? StateOf(int team, int squad) => _squads.TryGetValue((team, squad), out var s) ? s : null;

        /// <summary>Whether the monitor asked <paramref name="team"/>'s fire support to pick its anchors afresh (TacticalAi takes it).</summary>
        internal bool TakeAnchorRefresh(int team) => _anchorRefresh.Remove(team);

        /// <summary>A churning squad's commitment scale now (1 when not damped).</summary>
        public float CommitScale(int team, int squad, double now) =>
            _damped.TryGetValue((team, squad), out var until) && now < until ? Math.Max(1f, Tun.Health.ChurnCommitScale) : 1f;

        internal void Step()
        {
            var now = _world.Time;
            if (now < _next) return;
            _next = now + Math.Max(global::MachineBrigade.Sim.Content.SimTunables.Ai.AiHealthMonitor.StepPeriodSFloor, Tun.Health.PeriodS);
            var start = _world.AiPerf.Begin();
            Counters.Passes++;
            ReadLaneCounters(now);
            if (Tun.Health.Enabled)
            {
                Idle(now);
                Squads(now);
                Traffic(now);
            }
            _world.AiPerf.End(AiPerfSection.HealthMonitor, start);
        }

        // ------------------------------------------------------------------------------------------------ the counters

        private void ReadLaneCounters(double now)
        {
            var c = Counters;
            var watch = _world.CombatWatch;
            c.ArmedIdleWithoutReason = watch.Unexplained;
            c.CombatAnomalies = watch.Anomalies;
            var stats = _world.Traffic.Stats;
            c.SevereUnstuckEvents = stats.SevereUnstuck;
            c.DeadlockCycles = stats.Deadlocks;
            var brains = _world.Bosses.Brains;
            c.NavalReverseAttempts = brains.NavalReverseEvents + brains.NavalReverseRefused;
            if (brains.NavalReverseEvents > _lastNavalReverse)
            {
                // K1: a hard error in debug; the controller already clamped the speed (turn / slow / other lane instead).
                c.NavalReverseErrors += brains.NavalReverseEvents - _lastNavalReverse;
                _world.AiLog.Add(new DecisionEntry(now, -1, AiLayer.Commander, 0, DecisionKind.Emergency,
                    $"{P5Reasons.NavalReverseForbidden} events={brains.NavalReverseEvents} (error: speed clamped to 0)"));
                _lastNavalReverse = brains.NavalReverseEvents;
                if (Tun.Health.StrictAssertions) throw new InvalidOperationException("AI MASTER Part K: a boss ship tried to reverse (NAVAL_REVERSE_FORBIDDEN).");
            }
            // P0-B: a purchase without map influence is impossible by construction (rejected before scoring): counted at 0.
            c.NoMapInfluencePurchases = 0;
            // Churn rates from the decision log's totals (per minute over the last look).
            var (a, s, t) = _world.AiLog.Totals();
            if (!double.IsNaN(_lastChurnAt) && now > _lastChurnAt)
            {
                var minutes = (float)((now - _lastChurnAt) / 60.0);
                var squads = Math.Max(1, CountSquads());
                c.SquadActionSwitchesPerMinute = (a - _lastChurn.a) / minutes / squads;
                c.TargetSwitchesPerMinute = (t - _lastChurn.t) / minutes / squads;
            }
            _lastChurn = (a, s, t);
            _lastChurnAt = now;
            // Orders per unit per minute (AI sides; every unit order the world accepted for them).
            var orders = 0L;
            var units = 0;
            foreach (var team in Teams())
            {
                orders += _world.OrdersOf(team) - _ordersAt[team];
                _ordersAt[team] = _world.OrdersOf(team);
            }
            foreach (var v in _world.VehicleList)
                if (v.IsAlive && !v.Def.Static && _world.AiCommanders.ContainsKey(v.Team)) units++;
            if (!double.IsNaN(_ordersSince) && now > _ordersSince && units > 0)
                c.OrdersPerUnitPerMinute = (float)(orders / ((now - _ordersSince) / 60.0) / units);
            _ordersSince = now;
            // Low-utilisation unit classes (P4's same-match tracker).
            var low = 0;
            foreach (var team in Teams())
                if (_world.CoordinationIfAny?.Peek(team)?.PlanningIfAny is { } planning) low += planning.Adaptation.LowClasses(now);
            c.LowUtilizationUnitClasses = low;
            if (low > 0 && low != _lastLowClasses)
                _world.AiLog.Add(new DecisionEntry(now, -1, AiLayer.Commander, 0, DecisionKind.Hint, $"{P5Reasons.LowUtilizationClasses} {low} (purchase modifier acts)"));
            _lastLowClasses = low;
        }

        private int CountSquads()
        {
            var n = 0;
            foreach (var team in Teams())
                n += _world.AiCommanders[team].Squads.Squads.Count;
            return n;
        }

        /// <summary>The AI sides with a commander, in team order (deterministic).</summary>
        private IEnumerable<int> Teams()
        {
            for (var team = 0; team < 3; team++)
                if (_world.AiCommanders.ContainsKey(team)) yield return team;
        }

        // ------------------------------------------------------------------------------------------------ K1 idle armed units

        private void Idle(double now)
        {
            var watch = _world.CombatWatch;
            var fresh = watch.Unexplained - _lastUnexplained;
            _lastUnexplained = watch.Unexplained;
            foreach (var team in Teams())
            {
                Array.Clear(_idleByReason, 0, _idleByReason.Length);
                int armed = 0, bad = 0;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != team || v.Def.Passive || v.Def.Obstacle || v.Dummy) continue;
                    armed++;
                    var r = watch.ReasonOf(v.Id);
                    _idleByReason[(int)r]++;
                    if (!CombatReasons.Explains(r)) bad++;
                }
                if (!HealthRules.IdleTrips(bad + (fresh > 0 ? 1 : 0), armed)) continue;
                // Force a target / firing-solution audit and refresh the combat state of the units without a reason.
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != team || CombatReasons.Explains(watch.ReasonOf(v.Id))) continue;
                    v.RetargetAt = double.NegativeInfinity;
                    foreach (var w in v.Weapons) w.RetargetAt = double.NegativeInfinity;
                }
                Counters.IdleAudits++;
                _world.AiLog.Add(new DecisionEntry(now, team, AiLayer.Commander, 0, DecisionKind.Emergency, $"{P5Reasons.IdleAudit} idle={bad}/{armed}"));
                _world.AiLog.Add(new DecisionEntry(now, team, AiLayer.Commander, 0, DecisionKind.Hint, $"{P5Reasons.IdleTopReasons} {TopReasons()}"));
            }
        }

        private string TopReasons()
        {
            var parts = new List<string>();
            for (var k = 0; k < 3; k++)
            {
                int best = -1, n = 0;
                for (var i = 0; i < _idleByReason.Length; i++)
                {
                    var r = (CombatIdleReason)i;
                    if (r is CombatIdleReason.Active or CombatIdleReason.Firing or CombatIdleReason.Moving) continue;
                    if (_idleByReason[i] > n)
                    {
                        n = _idleByReason[i];
                        best = i;
                    }
                }
                if (best < 0) break;
                parts.Add($"{CombatReasons.Code((CombatIdleReason)best)}={n}");
                _idleByReason[best] = 0;
            }
            return parts.Count > 0 ? string.Join(" ", parts) : "none";
        }

        // ------------------------------------------------------------------------------------------------ K1 squads

        private void Squads(double now)
        {
            var noDamage = 0;
            var stalled = 0;
            foreach (var team in Teams())
            {
                var commander = _world.AiCommanders[team];
                var intel = _world.Intel.For(team);
                foreach (var s in commander.Squads.Squads)
                {
                    if (s.MemberList.Count == 0) continue;
                    var sample = Sample(team, s, intel, commander);
                    if (!_squads.TryGetValue((team, s.Id), out var st)) _squads[(team, s.Id)] = st = new SquadHealthState();
                    var h = HealthRules.Evaluate(sample, st, now);
                    if ((h & SquadHealth.NoDamage) != 0) noDamage++;
                    if ((h & SquadHealth.StalledObjective) != 0) stalled++;
                    if (HealthRules.RecoveryDue(h, st, now))
                    {
                        st.RecoveredAt = now;
                        Recover(commander, s, h, now);
                    }
                    // K1 excessive churn: a longer commitment for a while.
                    if (_world.AiLog.Churning(team, s.Id, now) && CommitScale(team, s.Id, now) <= 1f)
                    {
                        _damped[(team, s.Id)] = now + Tun.Health.ChurnDampS;
                        Counters.ChurnDamps++;
                        P2Reasons.Squad(_world, team, s.Id, DecisionKind.Hint, P5Reasons.ChurnDamped, $"commit x{Tun.Health.ChurnCommitScale:0.0} for {Tun.Health.ChurnDampS:0} s");
                    }
                }
            }
            Counters.SquadsNoDamage = noDamage;
            Counters.StalledObjectiveAssignments = stalled;
        }

        private readonly Dictionary<(int team, int squad), SquadSample> _injected = new();

        /// <summary>Part R R8: an artificial picture for one squad (tests only): the monitor judges it instead of the observed one.</summary>
        internal void Inject(int team, int squad, SquadSample sample) => _injected[(team, squad)] = sample;

        internal void ClearInjected() => _injected.Clear();

        /// <summary>The observed picture of a squad (fog-fair: its own members and its side's contacts).</summary>
        internal SquadSample Sample(int team, Squad s, TeamIntel intel, AiCommander commander)
        {
            if (_injected.TryGetValue((team, s.Id), out var injected)) return injected;
            var sample = new SquadSample { Team = team, Squad = s.Id, Members = s.MemberList.Count, LastFireAt = double.NegativeInfinity };
            foreach (var id in s.MemberList)
                if (_world.TryGetVehicle(id, out var v) && v.LastFiredAt > sample.LastFireAt) sample.LastFireAt = v.LastFiredAt;
            var reach = s.Reach + Tun.Health.ContactMargin;
            foreach (var c in intel.Contacts)
                if (Vector2.DistanceSquared(c.Position, s.Centre) <= reach * reach && _world.Time - c.LastSeen < global::MachineBrigade.Sim.Content.SimTunables.Ai.AiHealthMonitor.SampleTimeMax)
                {
                    sample.InContact = true;
                    break;
                }
            if (s.Task.Objective is { } o)
            {
                sample.HasObjective = true;
                sample.ObjectiveDistance = Vector2.Distance(o, s.Centre);
            }
            sample.Holding = s.Task.Hold || s.Dodging || commander.Defending || s.Action == SquadAction.Hold;
            return sample;
        }

        /// <summary>
        /// K1 "squad no useful damage" / stalled assignment: re-evaluate through the existing paths only: the squad re-scores its
        /// action next tick as an idle reassessment (it may keep it), its goal is re-issued (a fresh route; the traffic layer picks
        /// corridors), its side's fire support picks its anchors afresh, and the log says why.
        /// </summary>
        private void Recover(AiCommander commander, Squad s, SquadHealth h, double now)
        {
            s.HealthReassess = true;
            s.IssuedGoal = new Vector2(float.NaN, float.NaN);
            if ((h & SquadHealth.NoDamage) != 0) _anchorRefresh.Add(commander.Team);
            Counters.SquadReevaluations++;
            var code = (h & SquadHealth.NoDamage) != 0 ? P5Reasons.SquadZeroUtilization : P5Reasons.SquadStalledObjective;
            P2Reasons.Squad(_world, commander.Team, s.Id, DecisionKind.Emergency, code,
                $"{s.State} {s.Action} members={s.MemberList.Count}: re-evaluate {((h & SquadHealth.NoDamage) != 0 ? "anchor, route, mission" : "route, mission")}");
        }

        // ------------------------------------------------------------------------------------------------ K1 traffic

        private void Traffic(double now)
        {
            var blockedAll = 0;
            var movingAll = 0;
            foreach (var team in Teams())
            {
                int blocked = 0, moving = 0;
                foreach (var v in _world.VehicleList)
                {
                    if (!v.IsAlive || v.Team != team || v.Def.Static || v.Flying || v.Def.Naval != null) continue;
                    if (!v.HasPath && !v.IsMoving) continue;
                    moving++;
                    if (v.Traffic.Jam.Stage >= JamStage.Yield) blocked++;
                }
                blockedAll += blocked;
                movingAll += moving;
                if (!HealthRules.BlockedTrips(blocked, moving)) continue;
                // Congestion escalation: the squads with half or more of their members jammed re-issue their goals (the traffic
                // coordinator's corridor replan and predictive congestion pick another way) and re-score.
                var commander = _world.AiCommanders[team];
                var escalated = 0;
                foreach (var s in commander.Squads.Squads)
                {
                    var jammed = 0;
                    foreach (var id in s.MemberList)
                        if (_world.TryGetVehicle(id, out var v) && v.Traffic.Jam.Stage >= JamStage.Yield) jammed++;
                    if (jammed * global::MachineBrigade.Sim.Content.SimTunables.Ai.AiHealthMonitor.TrafficJammedScale < Math.Max(1, s.MemberList.Count)) continue;
                    if (!_squads.TryGetValue((team, s.Id), out var st)) _squads[(team, s.Id)] = st = new SquadHealthState();
                    if (now - st.RecoveredAt < Tun.Health.RecoveryCooldownS) continue;
                    st.RecoveredAt = now;
                    s.HealthReassess = true;
                    s.IssuedGoal = new Vector2(float.NaN, float.NaN);
                    escalated++;
                }
                Counters.TrafficEscalations++;
                _world.AiLog.Add(new DecisionEntry(now, team, AiLayer.Commander, 0, DecisionKind.Traffic,
                    $"{P5Reasons.TrafficEscalation} blocked={blocked}/{moving} squads={escalated}"));
            }
            Counters.BlockedUnits = blockedAll;
            Counters.BlockedRatio = movingAll > 0 ? blockedAll / (float)movingAll : 0f;
        }
    }
}
