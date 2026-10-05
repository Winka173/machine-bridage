#nullable enable
using MachineBrigade.Sim.AI;

namespace MachineBrigade.Sim
{
    /// <summary>AI MASTER P0-A (lane A): the combat activity watchdog (Part C) and the target accessibility cache (spec 47, 83).</summary>
    public sealed partial class SimWorld
    {
        private CombatActivityWatchdog? _combatWatch;
        private TargetAccessCache? _targetAccess;

        /// <summary>Part C: every armed unit's combat activity, its idle reason code and the automatic recovery.</summary>
        public CombatActivityWatchdog CombatWatch => _combatWatch ??= new CombatActivityWatchdog(this);

        /// <summary>
        /// Spec 47 / 83: whether a unit can get a firing solution on a point (cached per region and grid version). P0 wiring:
        /// answered by P0-B's reachable firing region (<see cref="EngagementFeasibility.CanFireFromComponent"/>).
        /// </summary>
        public TargetAccessCache TargetAccess => _targetAccess ??= new TargetAccessCache(this)
        {
            Resolver = (domain, component, target, radius, minRange, maxRange) =>
                Feasibility.CanFireFromComponent(domain, component, target, radius, minRange, maxRange),
        };
    }
}
