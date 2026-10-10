#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>One scout's mark on a target: who holds it, for which side, and the tick it lapses (exclusive).</summary>
    internal struct DesignationSlot
    {
        public Vehicle? Owner;
        public int Team;
        public long UntilTick;
    }

    public sealed partial class Vehicle
    {
        /// <summary>Scout Target Designation: the marks on this vehicle (one slot per marking scout; null until first marked).</summary>
        internal DesignationSlot[]? DesignationSlots;

        /// <summary>Scout Target Designation: the target this scout keeps marked (none if it has none).</summary>
        internal EntityId DesignationTarget;

        /// <summary>Scout Target Designation: the tick this scout next picks and refreshes its target (0: not scheduled yet).</summary>
        internal long DesignationNextTick;
    }
}
