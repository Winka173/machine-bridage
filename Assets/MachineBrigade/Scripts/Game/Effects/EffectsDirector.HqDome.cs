using System.Collections.Generic;
using MachineBrigade.Sim;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Prompt 32 L4 (lead UI pass 2026-10-02): the Shield HQ's emergency dome over its base, drawn with the same hex dome as
    /// the Shield Dome item and the shield carriers (<see cref="ShieldVisual"/>): the HQ types' radius across, half as high,
    /// in its side's colour. It rises when the sim's <c>HqState.DomeUp</c> turns on, flickers more as <c>DomeHp</c> runs
    /// low, gives a soft pulse when it soaks a hit (its health drops) and shatters with a ring when it breaks or runs out.
    /// The sim emits no hit event for this dome, so there is no ripple at the impact point. View only: reads the bases.
    /// </summary>
    public sealed partial class EffectsDirector
    {
        private sealed class HqDome
        {
            public ShieldVisual Shield;
            public float Radius;
            public bool Up;
            public float LastHp;
        }

        private readonly Dictionary<int, HqDome> _hqDomes = new();

        /// <summary>Every frame after <see cref="Tick"/>: each base's emergency dome, up or down as the sim says.</summary>
        public void TickHqDomes(SimWorld world, int playerTeam)
        {
            if (world?.Bases == null) return;
            var now = Time.time;
            var t = world.Time;
            var radius = world.Catalog.Base.HqTypes.Radius;
            foreach (var b in world.Bases.All)
            {
                var s = b.Hq32;
                var up = !b.HqFallen && s.DomeUp(t);
                if (!_hqDomes.TryGetValue(b.Team, out var dome))
                {
                    if (!up) continue;
                    var shield = new ShieldVisual("HQ Dome " + b.Team, _root, ShieldVisual.Shape.Dome, radius);
                    shield.Transform.localScale = new Vector3(radius, radius * ItemDomeHeight, radius);
                    shield.SetSide(b.Team == playerTeam);
                    dome = new HqDome { Shield = shield, Radius = radius };
                    _hqDomes[b.Team] = dome;
                }
                var centre = new Vector3(b.HqPosition.X, 0.05f, b.HqPosition.Y);
                dome.Shield.Transform.position = centre;
                if (up && !dome.Up)
                {
                    dome.Up = true;
                    dome.LastHp = s.DomeHp;
                    dome.Shield.Raise(now);
                    Ring(centre, dome.Radius * 2f, ShieldVisual.SideColour(b.Team == playerTeam));
                }
                else if (!up && dome.Up)
                {
                    dome.Up = false;
                    dome.Shield.Collapse(now);
                    Ring(centre, dome.Radius * 2f, Color.white);
                }
                if (dome.Up)
                {
                    var share = s.DomeFull > 0f ? s.DomeHp / s.DomeFull : 0f;
                    dome.Shield.Flicker = Mathf.Clamp01((0.4f - share) * 1.8f);
                    // A soaked hit: a short flare on the crown (where the eye looks; the sim gives no impact point).
                    if (s.DomeHp < dome.LastHp - 1f)
                    {
                        var strength = Mathf.Clamp((dome.LastHp - s.DomeHp) / 250f, 0.5f, 1.6f);
                        var crown = centre + Vector3.up * (dome.Radius * ItemDomeHeight);
                        dome.Shield.Hit(crown, now, default, strength);
                    }
                    dome.LastHp = s.DomeHp;
                }
                dome.Shield.Tick(now);
            }
        }
    }
}
