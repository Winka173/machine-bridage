#nullable enable
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// AI MASTER P5 (lane A): the battle's AI Health Monitor (Part K), the AI timing counters (Part P) and the AI spatial index
    /// (section 98). None of them feeds back into the battle except the monitor's valid re-evaluation requests.
    /// </summary>
    public sealed partial class SimWorld
    {
        private AiHealthMonitor? _health;
        private AiPerfCounters? _aiPerf;
        private AiSpatialIndex? _spatial;
        private readonly long[] _ordersP5 = new long[3];

        /// <summary>Part K: the AI Health Monitor (counters, squad health, recoveries).</summary>
        public AiHealthMonitor Health => _health ??= new AiHealthMonitor(this);

        /// <summary>Part P: per-system timing counters (set <see cref="AiPerfCounters.Enabled"/> to measure).</summary>
        public AiPerfCounters AiPerf => _aiPerf ??= new AiPerfCounters();

        /// <summary>Section 98: the AI's uniform grid over the living vehicles (rebuilt at most once a step).</summary>
        public AiSpatialIndex Spatial => _spatial ??= new AiSpatialIndex(this);

        /// <summary>Unit orders the world was asked for by <paramref name="team"/> so far (Part K ordersPerUnitPerMinute).</summary>
        public long OrdersOf(int team) => team >= 0 && team < _ordersP5.Length ? _ordersP5[team] : 0L;

        private void CountOrdersP5(Command command)
        {
            if (command.Team >= 0 && command.Team < _ordersP5.Length && command.Units != null) _ordersP5[command.Team] += command.Units.Count;
        }

        /// <summary>
        /// Spec 215 (P4 recorded, P5 shows): the tactical communication cues of <paramref name="team"/>'s AI (attack_go, flank,
        /// probe, feint, escape), oldest first; empty for a side without an AI planner. Presentation only, no gameplay effect.
        /// </summary>
        public System.Collections.Generic.IReadOnlyList<TacticalCue> CuesOf(int team) =>
            CoordinationIfAny?.Peek(team)?.PlanningIfAny?.Cues ?? (System.Collections.Generic.IReadOnlyList<TacticalCue>)System.Array.Empty<TacticalCue>();

        /// <summary>The health monitor's pass (it keeps its own 1 Hz clock); only where an AI side has a commander.</summary>
        private void StepP5()
        {
            if (AiCommanders.Count == 0 && _health == null) return;
            Health.Step();
        }
    }
}
