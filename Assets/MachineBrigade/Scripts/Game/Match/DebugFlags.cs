using System;
using System.Collections.Generic;
using UnityEngine;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Development switches read from the command line (on Android:
    /// <c>adb shell am start -n com.winka.machinebrigade/com.unity3d.player.UnityPlayerGameActivity --es mbflags -mb-no-shake,-mb-no-post</c>),
    /// so a rendering problem can be bisected on a device without a rebuild per experiment.
    /// In the editor they come from the Machine Brigade > Debug Flags window instead.
    /// </summary>
    public static class DebugFlags
    {
        /// <summary>Where the editor's Debug Flags window keeps its switches (EditorPrefs, comma-separated).</summary>
        public const string EditorPrefsKey = "MachineBrigade.DebugFlags";

        private static HashSet<string> _flags;

        /// <summary>The editor keeps statics between Play sessions (domain reload is off); start clean.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetStatics()
        {
            _flags = null;
        }

        public static bool Has(string flag)
        {
            if (_flags == null)
            {
                _flags = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                try
                {
                    foreach (var arg in Environment.GetCommandLineArgs()) Add(arg);
#if UNITY_EDITOR
                    Add(UnityEditor.EditorPrefs.GetString(EditorPrefsKey, ""));
#endif
#if UNITY_ANDROID && !UNITY_EDITOR
                    // IL2CPP players do not see intent extras on the command line; read ours directly.
                    using var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
                    using var activity = player.GetStatic<AndroidJavaObject>("currentActivity");
                    using var intent = activity.Call<AndroidJavaObject>("getIntent");
                    Add(intent.Call<string>("getStringExtra", "mbflags"));
#endif
                }
                catch (Exception e)
                {
                    Debug.LogWarning($"[DebugFlags] Could not read the command line: {e.Message}");
                }
                if (_flags.Count > 0) Debug.Log("[DebugFlags] " + string.Join(" ", _flags));
            }
            return _flags.Contains(flag);
        }

        private static void Add(string text)
        {
            if (string.IsNullOrEmpty(text)) return;
            foreach (var part in text.Split(new[] { ' ', ',' }, StringSplitOptions.RemoveEmptyEntries))
                if (part.StartsWith("-mb-", StringComparison.OrdinalIgnoreCase)) _flags.Add(part);
        }
    }
}
