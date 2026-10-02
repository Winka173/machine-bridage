using UnityEngine;

namespace MachineBrigade.Game.Audio
{
    /// <summary>
    /// Fix pass L7: the limiter at the end of the mix, on the AudioListener (the project has no AudioMixer asset: one cannot
    /// be authored outside the Unity editor, so the groups and the Effects compressor are in code, AudioDirector, and this
    /// is the output's brick wall). A peak follower with an instant attack and a 120 ms release: no sample leaves above
    /// <see cref="SoundLibrary.LimiterCeiling"/> (-1 dBFS), and under it nothing is touched. The music peaks well under the
    /// ceiling, so in practice it limits the effects only (the big blasts landing together).
    /// </summary>
    [DisallowMultipleComponent]
    internal sealed class EffectsLimiter : MonoBehaviour
    {
        private const float ReleaseSeconds = 0.12f;

        private float _envelope;
        private float _release = 0.9995f;

        /// <summary>The deepest gain reduction since the last read (linear, 1 = none): for the stress check and the tests.</summary>
        public float Reduction { get; private set; } = 1f;

        private void Awake()
        {
            var rate = Mathf.Max(8000, AudioSettings.outputSampleRate);
            _release = Mathf.Exp(-1f / (ReleaseSeconds * rate));
        }

        /// <summary>Reads and resets <see cref="Reduction"/>.</summary>
        public float TakeReduction()
        {
            var r = Reduction;
            Reduction = 1f;
            return r;
        }

        private void OnAudioFilterRead(float[] data, int channels)
        {
            if (channels <= 0) return;
            var ceiling = SoundLibrary.LimiterCeiling;
            var envelope = _envelope;
            var deepest = Reduction;
            for (var i = 0; i < data.Length; i += channels)
            {
                var peak = 0f;
                for (var c = 0; c < channels; c++)
                {
                    var a = data[i + c] < 0f ? -data[i + c] : data[i + c];
                    if (a > peak) peak = a;
                }
                envelope = peak > envelope ? peak : envelope * _release;
                if (envelope <= ceiling) continue;
                var gain = ceiling / envelope;
                if (gain < deepest) deepest = gain;
                for (var c = 0; c < channels; c++) data[i + c] *= gain;
            }
            _envelope = envelope;
            Reduction = deepest;
        }
    }
}
