#nullable enable
using System;
using System.Collections.Generic;

namespace MachineBrigade.Sim.Content
{
    /// <summary>
    /// Prompt 30 L2/L7: one line of the in-battle script (Resources/Data/script/chNN.json, built by
    /// Tools/story/script_build.py from Tools/story/script/chNN.txt): the mission, the trigger (a key of the sheet "Điểm
    /// kích hoạt"), its argument, the speaker, the priority (1-4 = P1-P4; P0 is a system warning, never a line), whether
    /// it plays once, its text key and both languages. The Game layer shows it; the battle is not changed.
    /// </summary>
    public sealed class ScriptLineDef
    {
        public string Mission { get; internal set; } = "";
        public string TriggerKey { get; internal set; } = "";
        public RadioTrigger Trigger { get; internal set; }
        public string? Arg { get; internal set; }
        public string Speaker { get; internal set; } = "hq";
        public int Priority { get; internal set; } = 2;
        public bool Once { get; internal set; } = true;
        public string Key { get; internal set; } = "";
        public string En { get; internal set; } = "";
        public string Vi { get; internal set; } = "";

        /// <summary>Seconds into the mission for a "time" line.</summary>
        public float Seconds { get; internal set; }
    }

    /// <summary>A character's role in the script (sheet "Giọng nhân vật"): what they speak about and on which triggers.</summary>
    public sealed class SpeakerDef
    {
        public string Id { get; internal set; } = "";
        public IReadOnlyList<string> Roles { get; internal set; } = Array.Empty<string>();
        public IReadOnlyList<string> Triggers { get; internal set; } = Array.Empty<string>();
    }

    /// <summary>The whole script: lines by mission, the speakers' roles, and the trigger keys.</summary>
    public sealed class StoryScript
    {
        /// <summary>The sheet's trigger keys and the radio trigger each one fires on.</summary>
        public static readonly IReadOnlyDictionary<string, RadioTrigger> TriggerKeys = new Dictionary<string, RadioTrigger>
        {
            ["mission_start"] = RadioTrigger.Start,
            ["time"] = RadioTrigger.Time,
            ["phase_start"] = RadioTrigger.Stage,
            ["phase_end"] = RadioTrigger.PhaseEnd,
            ["objective_progress"] = RadioTrigger.ObjectiveProgress,
            ["point_captured"] = RadioTrigger.Capture,
            ["point_lost"] = RadioTrigger.Lost,
            ["boss_spawn"] = RadioTrigger.Boss,
            ["boss_phase_change"] = RadioTrigger.BossPhase,
            ["boss_part_destroyed"] = RadioTrigger.BossPart,
            ["boss_hp"] = RadioTrigger.BossHp,
            ["superweapon_warning"] = RadioTrigger.Superweapon,
            ["general_tactic_change"] = RadioTrigger.TacticChange,
            ["expensive_unit_lost"] = RadioTrigger.ExpensiveLost,
            ["first_unit_type_seen"] = RadioTrigger.FirstSeen,
            ["hq_below_50"] = RadioTrigger.HqHalf,
            ["critical_failure_imminent"] = RadioTrigger.Critical,
            ["momentum_high_once"] = RadioTrigger.Momentum,
            ["ally_arrives"] = RadioTrigger.AllyArrives,
            ["ally_late"] = RadioTrigger.AllyLate,
            ["enemy_reinforcement"] = RadioTrigger.Reinforce,
            ["neutral_captured"] = RadioTrigger.NeutralCaptured,
            ["event_triggered"] = RadioTrigger.EventTriggered,
            ["objective_stall_90s"] = RadioTrigger.ObjectiveStall,
            ["timer_60s"] = RadioTrigger.Timer60,
            ["victory"] = RadioTrigger.Win,
            ["defeat"] = RadioTrigger.Lose,
        };

        private readonly Dictionary<string, List<ScriptLineDef>> _byMission = new();
        private readonly Dictionary<string, string> _main = new();
        private readonly Dictionary<string, SpeakerDef> _speakers = new();

        public IReadOnlyDictionary<string, SpeakerDef> Speakers => _speakers;

        /// <summary>Triggers any mission's main speaker may take (sheet: "Người nói chính", "Theo kịch bản").</summary>
        public IReadOnlyList<string> MainTriggers { get; private set; } = Array.Empty<string>();

        /// <summary>Triggers anyone may take when the script says so ("Theo kịch bản", "Theo sự kiện").</summary>
        public IReadOnlyList<string> ScriptedTriggers { get; private set; } = Array.Empty<string>();

        private static readonly IReadOnlyList<ScriptLineDef> None = Array.Empty<ScriptLineDef>();

        public IReadOnlyList<ScriptLineDef> For(string mission) => _byMission.TryGetValue(mission, out var l) ? l : None;

        /// <summary>The mission's main speaker (L5), or null.</summary>
        public string? MainSpeaker(string mission) => _main.TryGetValue(mission, out var s) ? s : null;

        public IEnumerable<ScriptLineDef> All
        {
            get
            {
                foreach (var list in _byMission.Values)
                    foreach (var l in list) yield return l;
            }
        }

        /// <summary>Adds the speakers file (Resources/Data/script/speakers.json).</summary>
        public void AddSpeakers(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "speakers");
            var speakers = root.Object("speakers");
            foreach (var id in speakers.Keys)
            {
                var o = speakers.Object(id);
                _speakers[id] = new SpeakerDef { Id = id, Roles = o.StringArray("roles"), Triggers = o.StringArray("triggers") };
            }
            MainTriggers = root.StringArray("mainTriggers");
            ScriptedTriggers = root.StringArray("scriptedTriggers");
        }

        /// <summary>Adds one chapter's file.</summary>
        public void AddChapter(string json, string path)
        {
            var root = new JsonObject(MiniJson.Parse(json), path);
            if (root.Has("missions"))
            {
                var missions = root.Object("missions");
                foreach (var id in missions.Keys)
                    if (missions.Object(id).OptionalString("main") is { } main) _main[id] = main;
            }
            foreach (var o in root.Array("lines"))
            {
                var key = o.String("trigger");
                if (!TriggerKeys.TryGetValue(key, out var trigger)) throw new FormatException($"{o.Path}: unknown trigger {key}");
                var line = new ScriptLineDef
                {
                    Mission = o.String("mission"),
                    TriggerKey = key,
                    Trigger = trigger,
                    Arg = o.OptionalString("arg"),
                    Speaker = o.String("speaker"),
                    Priority = o.Int("priority", 2),
                    Once = o.Bool("once", true),
                    Key = o.String("key"),
                    En = o.String("en"),
                    Vi = o.String("vi"),
                    Seconds = o.Float("at", 0f),
                };
                if (!_byMission.TryGetValue(line.Mission, out var list)) _byMission[line.Mission] = list = new List<ScriptLineDef>();
                list.Add(line);
            }
        }
    }
}
