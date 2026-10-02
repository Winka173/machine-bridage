#nullable enable
using System;
using System.Numerics;

namespace MachineBrigade.Sim
{
    /// <summary>
    /// Prompt 31 L3 (the sandstorm turning): the storm over one half of the map. Inside the half every spotter's reach is
    /// multiplied by <see cref="StormInside"/>, outside it by <see cref="StormOutside"/> (the far half may clear); both are 1
    /// when there is no storm. The half is the side of the line through <see cref="StormOrigin"/> that
    /// <see cref="StormNormal"/> points to. Set by the event system as the wind turns; in the battle's fingerprint.
    /// </summary>
    public sealed partial class SimWorld
    {
        public bool StormActive { get; private set; }
        public Vector2 StormNormal { get; private set; } = Vector2.UnitX;
        public Vector2 StormOrigin { get; private set; }
        public float StormInside { get; private set; } = 1f;
        public float StormOutside { get; private set; } = 1f;

        /// <summary>Whether a point is under the storm's half.</summary>
        public bool InStorm(Vector2 p) => StormActive && Vector2.Dot(p - StormOrigin, StormNormal) > 0f;

        /// <summary>The storm's factor on a spotter standing at <paramref name="p"/> (1: no storm).</summary>
        public float StormSight(Vector2 p) => !StormActive ? 1f : InStorm(p) ? StormInside : StormOutside;

        internal void SetStorm(Vector2 origin, Vector2 normal, float inside, float outside)
        {
            StormOrigin = origin;
            StormNormal = normal.LengthSquared() > 1e-6f ? Vector2.Normalize(normal) : Vector2.UnitX;
            StormInside = Math.Clamp(inside, 0.3f, 1.5f);
            StormOutside = Math.Clamp(outside, 0.3f, 1.5f);
            StormActive = MathF.Abs(StormInside - 1f) > 1e-3f || MathF.Abs(StormOutside - 1f) > 1e-3f;
        }

        internal void MixStorm(Action<long> mix)
        {
            if (!StormActive) return;
            mix((long)Math.Round(StormInside * 1000f) * 4096 + (long)Math.Round(StormOutside * 1000f));
            mix((long)Math.Round(StormNormal.X * 100f) * 1000 + (long)Math.Round(StormNormal.Y * 100f));
        }
    }
}
