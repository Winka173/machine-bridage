using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Hud
{
    /// <summary>
    /// Prompt 30 L7: the in-battle script (Resources/Data/script: speakers.json and one chNN.json per chapter, built by
    /// Tools/story/script_build.py). Loaded on first use; its lines' texts join the string table (both languages).
    /// </summary>
    public static class ScriptText
    {
        private static StoryScript _script;
        private static Dictionary<string, (string en, string vi)> _table;

        public static StoryScript Script
        {
            get
            {
                if (_script != null) return _script;
                _script = new StoryScript();
                var speakers = Resources.Load<TextAsset>("Data/script/speakers");
                if (speakers != null) _script.AddSpeakers(speakers.text);
                foreach (var file in Resources.LoadAll<TextAsset>("Data/script"))
                    if (file.name.StartsWith("ch")) _script.AddChapter(file.text, "script/" + file.name);
                return _script;
            }
        }

        /// <summary>The script's texts by key.</summary>
        public static IReadOnlyDictionary<string, (string en, string vi)> Table
        {
            get
            {
                if (_table != null) return _table;
                _table = new Dictionary<string, (string en, string vi)>();
                foreach (var line in Script.All) _table[line.Key] = (line.En, line.Vi);
                return _table;
            }
        }

        public static bool TryGet(string key, out (string en, string vi) text) => Table.TryGetValue(key, out text);
    }
}
