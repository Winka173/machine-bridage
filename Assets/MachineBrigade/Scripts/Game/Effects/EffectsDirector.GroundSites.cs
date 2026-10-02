using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 31 (lead UI pass 2026-10-02): the flames and smoke the closed-ground looks feed (<see cref="Views.GroundSiteView"/>:
    /// a burning forest strip, a lava cut). The same emitters as a burning hull's, skipped off screen. View only.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        /// <summary>A lick of flame standing on the ground at <paramref name="at"/> (a burning strip's, a lava cut's).</summary>
        public void GroundFire(Vector3 at, float size)
        {
            if (!_cull.Visible(at, 0.2f)) return;
            _emitters.DamageFire(at, size);
        }

        /// <summary>A billow of smoke off burning ground; <paramref name="shade"/> 1 is pale grey, 0 black.</summary>
        public void GroundSmoke(Vector3 at, float size, float shade)
        {
            if (!_cull.Visible(at, 0.35f)) return;
            _emitters.DamageSmoke(at, size, shade);
        }

        /// <summary>A puff of dust where closed ground has just come in (a fallen boom, a collapsing adit).</summary>
        public void GroundDust(Vector3 at, float scale)
        {
            if (!_cull.Visible(at, 0.2f)) return;
            _emitters.Dust(at, scale);
        }
    }
}
