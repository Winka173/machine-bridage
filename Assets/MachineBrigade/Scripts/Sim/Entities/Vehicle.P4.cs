#nullable enable

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>
        /// AI MASTER P4: an AI air package (SEAD hold, CAP, handoff, bomber wait) owns this aircraft's orders this look; the old
        /// TacticalAi air logic leaves it alone (intent ownership). Set and cleared by the side's commander once a second.
        /// </summary>
        internal bool P4Held;
    }
}
