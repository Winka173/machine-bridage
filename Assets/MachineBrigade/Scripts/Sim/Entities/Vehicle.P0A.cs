#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    public sealed partial class Vehicle
    {
        /// <summary>
        /// AI MASTER P0-A (Part C1 step 6): a target the combat watchdog gave up on (target, solution and a ready weapon, yet
        /// no shot twice running): the weapons take it only as a last resort until <see cref="SuppressedUntil"/>.
        /// </summary>
        internal EntityId SuppressedTarget;
        internal double SuppressedUntil = double.NegativeInfinity;
    }
}
