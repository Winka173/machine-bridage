#nullable enable
namespace MachineBrigade.Sim
{
    /// <summary>
    /// AI MASTER P2 (lane C): the battle-wide services of the role / mode lane: the mode doctrine and its phase (Part I), the
    /// component-state record (Part F), the friendly firing-lane resolver (Part E) and the cover reservations (Part D5).
    /// Created on first use; nothing here steps on its own.
    /// </summary>
    public sealed partial class SimWorld
    {
        private AI.ModeDoctrineState? _doctrineP2;
        private AI.ComponentWatch? _componentsP2;
        private AI.FiringLaneResolver? _firingLanesP2;
        private AI.PositionReservations? _positionsP2;

        /// <summary>Part I: the mode doctrine now and its phase generation.</summary>
        public AI.ModeDoctrineState Doctrine => _doctrineP2 ??= new AI.ModeDoctrineState(this);

        /// <summary>Part F: what each vehicle can still do.</summary>
        public AI.ComponentWatch Components => _componentsP2 ??= new AI.ComponentWatch(this);

        /// <summary>Part E: blocked-shot handling.</summary>
        internal AI.FiringLaneResolver FiringLanes => _firingLanesP2 ??= new AI.FiringLaneResolver(this);

        /// <summary>Part D5: reserved firing positions.</summary>
        internal AI.PositionReservations Positions => _positionsP2 ??= new AI.PositionReservations(this);
    }
}
