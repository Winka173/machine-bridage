using MachineBrigade.Game.Match;
using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Play-test 8 (DECISIONS 22R): the light of burning vehicles on their own hull and on the ground round them, the
    /// warm glow War Thunder and World of Tanks throw from a burning tank. Not Unity lights (each would cost the phone a
    /// pass or a light-list slot): up to <see cref="Max"/> glows (<see cref="LowMax"/> on Low) handed to the Lit shader
    /// as global arrays (<c>_MbHeat</c>: position and 1 / reach², <c>_MbHeatColour</c>, <c>_MbHeatCount</c>), which adds
    /// each one's warm light with a soft fall-off, no shadows, on everything it lights. With nothing burning the count is
    /// 0 and the shader's loop does no work. EffectsDirector gathers them every frame (<see cref="Begin"/>, HullFire.Light,
    /// <see cref="Commit"/>): the worst fires win when more burn at once.
    /// </summary>
    internal static class HeatLights
    {
        public const int Max = 4, LowMax = 2;

        private static readonly int HeatId = Shader.PropertyToID("_MbHeat");
        private static readonly int ColourId = Shader.PropertyToID("_MbHeatColour");
        private static readonly int CountId = Shader.PropertyToID("_MbHeatCount");

        private static readonly Vector4[] At = new Vector4[Max];
        private static readonly Vector4[] Colour = new Vector4[Max];
        private static readonly float[] Power = new float[Max];
        private static int _count;

        /// <summary>The fire's colour (linear), times its power and flicker.</summary>
        public static readonly Color Warm = new(1f, 0.36f, 0.07f);

        /// <summary>Glows added since <see cref="Begin"/>.</summary>
        public static int Count => _count;

        /// <summary>The cap on this tier.</summary>
        public static int Cap => MatchSettings.Tier == GraphicsQuality.Low ? LowMax : Max;

        public static void Begin() => _count = 0;

        /// <summary>
        /// A fire's glow at <paramref name="at"/>, reaching <paramref name="reach"/> metres at <paramref name="power"/>
        /// (about 2.5 to 6), flickering by <paramref name="seed"/> and <paramref name="time"/>. When the cap is reached it
        /// replaces the weakest glow if it is stronger.
        /// </summary>
        public static void Add(Vector3 at, float reach, float power, int seed, float time)
        {
            var slot = _count;
            if (_count >= Cap)
            {
                slot = 0;
                for (var i = 1; i < _count; i++)
                    if (Power[i] < Power[slot]) slot = i;
                if (Power[slot] >= power) return;
            }
            else _count++;
            var light = power * Flicker(seed, time);
            At[slot] = new Vector4(at.x, at.y, at.z, 1f / Mathf.Max(0.5f, reach * reach));
            Colour[slot] = new Vector4(Warm.r * light, Warm.g * light, Warm.b * light, 1f);
            Power[slot] = power;
        }

        /// <summary>
        /// A fire's flicker, 0.62 to 1.1: two noises, a fast one (the flames' ten beats a second) over a slow swell;
        /// the seed keeps two fires from pulsing together.
        /// </summary>
        public static float Flicker(int seed, float time)
        {
            var phase = (seed & 1023) * 0.173f;
            // MVA W1-B: reduced flashes keep only the slow swell (spec part AL: no rapid flicker).
            var fast = MatchSettings.ReducedFlash ? 0.5f : Mathf.PerlinNoise(time * 9f, phase);
            var slow = Mathf.PerlinNoise(time * 1.3f + phase, 7.1f);
            return 0.62f + 0.3f * fast + 0.18f * slow;
        }

        /// <summary>Hands the glows to the shaders.</summary>
        public static void Commit()
        {
            for (var i = _count; i < Max; i++) Colour[i] = Vector4.zero;
            Shader.SetGlobalVectorArray(HeatId, At);
            Shader.SetGlobalVectorArray(ColourId, Colour);
            Shader.SetGlobalFloat(CountId, _count);
        }

        /// <summary>No glows (a match ending, a shot finished).</summary>
        public static void Clear()
        {
            _count = 0;
            Commit();
        }
    }
}
