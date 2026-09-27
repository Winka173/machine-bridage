using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Match;
using UnityEditor;
using UnityEngine;

namespace MachineBrigade.Editor
{
    /// <summary>
    /// The development switches (<see cref="DebugFlags"/>) for Play mode in the editor, which has
    /// no command line to pass them on: tick them here and press Play. They are kept per machine
    /// in EditorPrefs and never reach a build.
    /// </summary>
    public sealed class DebugFlagsWindow : EditorWindow
    {
        private static readonly (string Flag, string Label)[] Modes =
        {
            ("", "(as chosen in the menu)"), ("-mb-defend", "Defend"), ("-mb-weekly", "Weekly fortress"),
            ("-mb-assault", "Breakthrough"), ("-mb-hill", "King of the Hill"), ("-mb-deathmatch", "Deathmatch"),
            ("-mb-siege", "Siege"), ("-mb-survival", "Survival"), ("-mb-bossrush", "Boss rush"),
        };

        private static readonly (string Flag, string Label)[] Weathers =
        {
            ("", "(as chosen in the menu)"), ("-mb-clear", "Clear"), ("-mb-rain", "Rain"), ("-mb-storm", "Storm"),
            ("-mb-snow", "Snow"), ("-mb-sandstorm", "Sandstorm"), ("-mb-fog", "Fog"), ("-mb-night", "Night"),
        };

        private static readonly (string Flag, string Label)[] Views =
        {
            ("-mb-towerwatch", "Tower watch: the camera on a defence as it is shot down in steps"),
            ("-mb-bastion", "Bastion watch: the camera on the camp bastion, with enemy raids"),
            ("-mb-smokescreen", "Smoke screens: blasts inside smoke every few seconds"),
            ("-mb-demolish", "Demolish: the building nearest the view comes down every few seconds"),
            ("-mb-overview", "Overview: the whole battlefield in one view"),
            ("-mb-far", "Far: the north-west corner, zoomed right out"),
            ("-mb-perf", "Performance probe"),
        };

        private static readonly (string Flag, string Label)[] Off =
        {
            ("-mb-no-shake", "Camera shake"), ("-mb-no-post", "Post-processing"), ("-mb-no-shadows", "Shadows"),
            ("-mb-no-fx", "Effects"), ("-mb-no-hud", "HUD"), ("-mb-no-cinematics", "Cinematic cameras"),
        };

        private HashSet<string> _flags;
        private Vector2 _scroll;

        [MenuItem("Machine Brigade/Debug Flags...")]
        private static void Open() => GetWindow<DebugFlagsWindow>("MB Debug Flags");

        private void OnEnable() => _flags = new HashSet<string>(
            EditorPrefs.GetString(DebugFlags.EditorPrefsKey, "").Split(',').Where(f => f.StartsWith("-mb-")));

        private void OnGUI()
        {
            _scroll = EditorGUILayout.BeginScrollView(_scroll);
            EditorGUILayout.HelpBox("Switches for Play mode in the editor (a device build reads them from the command line). " +
                                    "They apply the next time you press Play.", MessageType.Info);

            EditorGUILayout.LabelField("Start", EditorStyles.boldLabel);
            Toggle("-mb-play", "Start a battle straight away (skip the menu)");
            using (new EditorGUI.DisabledScope(!_flags.Contains("-mb-play")))
            {
                Choose("Mode", Modes.Concat(Campaign.All.Select(m => ("-mb-" + m.Id, "Campaign " + m.Id))).ToArray());
                Choose("Map", new[] { ("", "(as chosen in the menu)") }.Concat(MatchSettings.AllMaps.Select(m => ("-mb-" + m.Id, m.Id))).ToArray());
                Choose("Weather", Weathers);
            }

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Test views", EditorStyles.boldLabel);
            foreach (var (flag, label) in Views) Toggle(flag, label);

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Switch off", EditorStyles.boldLabel);
            foreach (var (flag, label) in Off) Toggle(flag, label);

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Active", _flags.Count == 0 ? "(none)" : string.Join(" ", _flags.OrderBy(f => f)), EditorStyles.wordWrappedLabel);
            if (GUILayout.Button("Clear all"))
            {
                _flags.Clear();
                Save();
            }
            EditorGUILayout.EndScrollView();
        }

        private void Toggle(string flag, string label)
        {
            var on = _flags.Contains(flag);
            var now = EditorGUILayout.ToggleLeft(label, on);
            if (now == on) return;
            if (now) _flags.Add(flag);
            else _flags.Remove(flag);
            Save();
        }

        /// <summary>One of a group of flags that exclude each other (a mode, a map, a weather).</summary>
        private void Choose(string label, (string Flag, string Label)[] options)
        {
            var current = 0;
            for (var i = 1; i < options.Length; i++)
                if (_flags.Contains(options[i].Flag)) current = i;
            var chosen = EditorGUILayout.Popup(label, current, options.Select(o => o.Label).ToArray());
            if (chosen == current) return;
            foreach (var (flag, _) in options)
                if (flag.Length > 0) _flags.Remove(flag);
            if (options[chosen].Flag.Length > 0) _flags.Add(options[chosen].Flag);
            Save();
        }

        private void Save() => EditorPrefs.SetString(DebugFlags.EditorPrefsKey, string.Join(",", _flags));
    }
}
