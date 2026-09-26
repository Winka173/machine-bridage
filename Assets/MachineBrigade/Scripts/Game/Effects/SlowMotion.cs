using UnityEngine;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// A brief slow-down on the biggest blasts. Because the simulation advances on scaled
    /// time, gameplay slows with the visuals and stays consistent. Cooldown-limited, and
    /// switched off by the Reduced motion setting.
    /// </summary>
    internal sealed class SlowMotion
    {
        private const float Cooldown = 5f;

        private float _until = -1f;
        private float _readyAt;

        public bool Enabled { get; set; } = true;

        public void Trigger(float realNow, float duration = 0.35f, float scale = 0.3f)
        {
            if (!Enabled || realNow < _readyAt) return;
            Time.timeScale = scale;
            _until = realNow + duration;
            _readyAt = realNow + Cooldown;
        }

        public void Tick(float realNow)
        {
            if (_until < 0f || realNow < _until) return;
            Time.timeScale = 1f;
            _until = -1f;
        }

        public void Reset()
        {
            Time.timeScale = 1f;
            _until = -1f;
        }
    }
}
