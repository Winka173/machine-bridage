#nullable enable
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Movement
{
    /// <summary>Prompt 25 F2 batch A (DECISIONS 25F2-A): the stand-off glide bomber's run.</summary>
    internal sealed partial class MovementSystem
    {
        /// <summary>A glide bomber breaks away once inside this share of its bombs' reach (it lets them go from further out).</summary>
        internal const float GlideBreak = 0.75f;

        /// <summary>
        /// A stand-off bomber never flies over its target: once inside <see cref="GlideBreak"/> of its glide bombs' reach it
        /// turns away and runs out (the run's extension), then comes round to release again from the edge of its reach.
        /// </summary>
        private static void GlideAway(Vehicle v, IDamageable target, float range, float distance)
        {
            if (v.RunExtending || distance >= range * GlideBreak) return;
            v.RunExtending = true;
            v.BreakAway = true;
            v.BreakHeading = SimMath.HeadingOf(v.Position - target.Position);
        }
    }
}
