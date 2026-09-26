using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Picks a frame rate the device can hold. Uneven frame times (33, 50, 33, 66 ms) read as
    /// stutter far more than a steady 30 fps does, so when a device cannot stay close to 60 the
    /// game settles at 30. When frame timing shows plenty of headroom again, it goes back to 60.
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

        public FrameRateGovernor(int start = 60) => Application.targetFrameRate = start;

        public int Target => Application.targetFrameRate;

        public void Tick()
        {
            var now = Time.realtimeSinceStartup;
            if (now < WarmUpSeconds) return;
            if (_windowStart < 0f) _windowStart = now;
            var dt = Time.unscaledDeltaTime;
            _frames++;
            _sum += dt;
            if (dt > (Target >= 60 ? 1f / 45f : 1f / 24f)) _slow++;
            FrameTimingManager.CaptureFrameTimings();
            if (now - _windowStart < WindowSeconds || _frames == 0) return;

            var fps = _frames / Mathf.Max(0.001f, _sum);
            var slowShare = _slow / (float)_frames;
            if (Target >= 60 && (fps < 50f || slowShare > 0.15f))
            {
                Application.targetFrameRate = 30;
                Debug.Log($"[Perf] frame rate 60 -> 30 (measured {fps:0.0} fps, {slowShare:P0} slow frames)");
            }
            else if (Target < 60)
            {
                // Only go back up when the work per frame clearly fits in 16 ms.
                var work = FrameTimingManager.GetLatestTimings(1, _timing) > 0
                    ? Mathf.Max((float)_timing[0].cpuFrameTime, (float)_timing[0].gpuFrameTime)
                    : float.MaxValue;
                _headroomWindows = work > 0f && work < 11f ? _headroomWindows + 1 : 0;
                if (_headroomWindows >= 3)
                {
                    Application.targetFrameRate = 60;
                    _headroomWindows = 0;
                    Debug.Log($"[Perf] frame rate 30 -> 60 (frame work {work:0.0} ms)");
                }
            }
            _windowStart = now;
            _frames = _slow = 0;
            _sum = 0f;
        }
    }
}
