using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Picks a frame rate the device can hold, up to the player's cap (30, 60 or 120). Uneven
    /// frame times (33, 50, 33, 66 ms) read as stutter far more than a steady lower rate does,
    /// so when a device cannot stay close to its target the game steps down (120 to 60 to 30).
    /// When frame timing shows plenty of headroom again, it steps back up towards the cap.
    /// (Lowering the render resolution was tried and dropped: on the emulator it blurred the
    /// picture without gaining a single frame.)
    /// </summary>
    internal sealed class FrameRateGovernor
    {
        private const float WindowSeconds = 4f;
        private const float WarmUpSeconds = 6f;

        private float _windowStart = -1f, _sum;
        private int _frames, _slow, _headroomWindows;
        private readonly FrameTiming[] _timing = new FrameTiming[1];

        private readonly float _created;
        private readonly int _cap;

        public FrameRateGovernor(int start = 60, int cap = 60)
        {
            _cap = Mathf.Max(30, cap);
            Application.targetFrameRate = Mathf.Min(start, _cap);
            // Measured from each scene load, so the hitch of loading a match never counts.
            _created = Time.realtimeSinceStartup;
        }

        public int Target => Application.targetFrameRate;

        public void Tick()
        {
            var now = Time.realtimeSinceStartup;
            if (now - _created < WarmUpSeconds) return;
            if (_windowStart < 0f) _windowStart = now;
            var dt = Time.unscaledDeltaTime;
            _frames++;
            _sum += dt;
            if (dt > 1f / (Target * 0.75f)) _slow++;
            FrameTimingManager.CaptureFrameTimings();
            if (now - _windowStart < WindowSeconds || _frames == 0) return;

            var fps = _frames / Mathf.Max(0.001f, _sum);
            var slowShare = _slow / (float)_frames;
            if (Target > 30 && (fps < Target * 0.83f || slowShare > 0.15f))
            {
                var lower = Target > 60 ? 60 : 30;
                Debug.Log($"[Perf] frame rate {Target} -> {lower} (measured {fps:0.0} fps, {slowShare:P0} slow frames)");
                Application.targetFrameRate = lower;
                _headroomWindows = 0;
            }
            else if (Target < _cap)
            {
                // Only go back up when the work per frame clearly fits the faster frame.
                var higher = Target < 60 ? 60 : _cap;
                var work = FrameTimingManager.GetLatestTimings(1, _timing) > 0
                    ? Mathf.Max((float)_timing[0].cpuFrameTime, (float)_timing[0].gpuFrameTime)
                    : 0f;
                // No timing data (some GPUs report none): judge by the frame time itself.
                if (work <= 0f) work = _sum / _frames * 1000f;
                _headroomWindows = work < 1000f / higher * 0.68f ? _headroomWindows + 1 : 0;
                if (_headroomWindows >= 3)
                {
                    Application.targetFrameRate = higher;
                    _headroomWindows = 0;
                    Debug.Log($"[Perf] frame rate -> {higher} (frame work {work:0.0} ms)");
                }
            }
            _windowStart = now;
            _frames = _slow = 0;
            _sum = 0f;
        }
    }
}
