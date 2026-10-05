#nullable enable
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// AI MASTER P3 (lane A): the coordination layer's battle-wide state (per side: frontline, tactical memory, the planned
    /// action board, the counter-battery tracker, attack packages). Created by the first AI commander that asks; until then the
    /// event hook below costs one null test per event.
    /// </summary>
    public sealed partial class SimWorld
    {
        private AI.CoordinationState? _coordinationP3;

        /// <summary>The P3 coordination state (made on first use).</summary>
        public AI.CoordinationState Coordination => _coordinationP3 ??= new AI.CoordinationState(this);

        /// <summary>The state if an AI has made it (the targeting reads it without creating it).</summary>
        internal AI.CoordinationState? CoordinationIfAny => _coordinationP3;

        /// <summary>Spec 129 / 144: own losses and observed enemy shells feed the AI memory (observation only, never a reveal).</summary>
        private void ObserveP3(in SimEvent e)
        {
            if (_coordinationP3 == null) return;
            if (e.Kind == SimEventKind.WeaponFired || e.Kind == SimEventKind.VehicleDestroyed || e.Kind == SimEventKind.PartBroken) _coordinationP3.Observe(e);
        }
    }
}
