using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Short vibrations on the heaviest moments (a boss falling, ultimate blasts on screen). Uses
    /// Android's amplitude-controlled one-shot where available, the plain buzz otherwise; silent in
    /// the editor and when switched off in Settings.
    /// </summary>
    public static class Haptics
    {
        private static float _lastPulse = -10f;

#if UNITY_ANDROID && !UNITY_EDITOR
        private static AndroidJavaObject _vibrator;
        private static AndroidJavaClass _effect;
        private static bool _ready, _amplitude;

        private static void Init()
        {
            if (_ready) return;
            _ready = true;
            try
            {
                using var unity = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
                using var activity = unity.GetStatic<AndroidJavaObject>("currentActivity");
                _vibrator = activity.Call<AndroidJavaObject>("getSystemService", "vibrator");
                using var version = new AndroidJavaClass("android.os.Build$VERSION");
                _amplitude = version.GetStatic<int>("SDK_INT") >= 26;
                if (_amplitude) _effect = new AndroidJavaClass("android.os.VibrationEffect");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Haptics] Unavailable: {e.Message}");
                _vibrator = null;
            }
        }
#endif

        /// <summary>A pulse of <paramref name="milliseconds"/> at <paramref name="strength"/> (1-255); at most one per 0.15 s.</summary>
        public static void Pulse(int milliseconds, int strength = 200)
        {
            if (!MatchSettings.Haptics || Time.unscaledTime - _lastPulse < 0.15f) return;
            _lastPulse = Time.unscaledTime;
#if UNITY_ANDROID && !UNITY_EDITOR
            Init();
            if (_vibrator == null) return;
            try
            {
                if (_amplitude)
                {
                    using var effect = _effect.CallStatic<AndroidJavaObject>("createOneShot", (long)milliseconds, Mathf.Clamp(strength, 1, 255));
                    _vibrator.Call("vibrate", effect);
                }
                else Handheld.Vibrate();
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Haptics] {e.Message}");
            }
#endif
        }
    }
}
