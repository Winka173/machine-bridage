#nullable enable
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Entities
{
    /// <summary>The tower-branch rework (DECISIONS 19T): a tower's own shield from a shield generator's "tower shields" branch.</summary>
    public sealed partial class Vehicle
    {
        /// <summary>What is left of its tower shield (0: none, or broken).</summary>
        public float WardHp { get; internal set; }

        /// <summary>The shield at full (the emitter's shield hit points, scaled like its health).</summary>
        public float WardFull { get; internal set; }

        /// <summary>The generator its shield comes from (none: no shield).</summary>
        public EntityId WardFrom { get; internal set; }

        internal double WardHitAt = double.NegativeInfinity;
    }
}
