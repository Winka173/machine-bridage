using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Cinematic moments for a boss dying: time eases down to a crawl for about a second and back,
    /// the camera leans in, and letterbox bars slide in so it reads as deliberate rather than as a
    /// stutter. Only bosses get one (ultimate explosions used to as well, which, every half minute
    /// in a big battle, read as the game hitching), and it can be switched off.
    /// </summary>
    internal sealed class Cinematics
    {
        private const float Cooldown = 25f;
        private const float EaseIn = 0.14f;
        private const float Hold = 0.95f;
        private const float EaseOut = 0.7f;
        private const float Slow = 0.28f;

        private float _start = -100f, _last = -100f;

        public bool Enabled { get; set; } = true;

        public Vector3 Focus { get; private set; }

        private float Length => EaseIn + Hold + EaseOut;

        public bool Active(float now) => now - _start < Length;

        /// <summary>Starts a moment at <paramref name="at"/>; <paramref name="force"/> skips the cooldown.</summary>
        public bool Trigger(Vector3 at, float now, bool force = false)
        {
            if (!Enabled || Active(now) || (!force && now - _last < Cooldown)) return false;
            _start = _last = now;
            Focus = at;
            return true;
        }

        /// <summary>The time scale for this moment (1 outside one).</summary>
        public float TimeScale(float now)
        {
            var t = now - _start;
            if (t < 0f || t >= Length) return 1f;
            if (t < EaseIn) return Mathf.Lerp(1f, Slow, Smooth(t / EaseIn));
            if (t < EaseIn + Hold) return Slow;
            return Mathf.Lerp(Slow, 1f, Smooth((t - EaseIn - Hold) / EaseOut));
        }

        /// <summary>How far the letterbox bars are in (0 to 1).</summary>
        public float Letterbox(float now)
        {
            var t = now - _start;
            if (t < 0f || t >= Length) return 0f;
            if (t < 0.25f) return Smooth(t / 0.25f);
            if (t > Length - 0.35f) return Smooth((Length - t) / 0.35f);
            return 1f;
        }

        private static float Smooth(float x)
        {
            x = Mathf.Clamp01(x);
            return x * x * (3f - 2f * x);
        }
    }
}
