using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Game.Match
{
    /// <summary>One line of radio chatter: who speaks (a portrait id) and the text's key.</summary>
    internal readonly struct RadioLine
    {
        public RadioLine(string speaker, string key)
        {
            Speaker = speaker;
            Key = key;
        }

        public string Speaker { get; }
        public string Key { get; }

        /// <summary>An enemy general is speaking.</summary>
        public bool Enemy => Speaker is "varga" or "orlov" or "kessler" or "sen" or "quaden" or "aurel";
    }

    /// <summary>
    /// The battle's radio chatter in a campaign mission: the mission's own lines when their moment
    /// comes (the start, a time, a point taken or lost, the boss arriving or half down, the HQ half
    /// down, a stage, the enemy reinforcing, the end), and when a moment has no line of its own,
    /// one of the brigade's usual ones, now and then. Radio messages the battle sends (stage events,
    /// a betrayal, a boss that flees) are spoken by whoever the key names. Each line plays once;
    /// what it shows is the HUD's business. Presentation only: nothing here touches the battle.
    /// </summary>
    internal sealed class RadioDirector
    {
        /// <summary>At least this long between two lines the director picks itself (the mission's own come when due).</summary>
        private const double GenericGap = 35.0;

        private static readonly HashSet<string> SpeakerIds = new(CampaignText.Speakers);

        /// <summary>Who speaks a key that names no speaker ("radio.betrayal").</summary>
        private static readonly Dictionary<string, string> Voices = new()
        {
            ["radio.betrayal"] = "linh",
            ["radio.bossFled"] = "khai",
            ["radio.alliedStrikes"] = "dieuhau",
            ["radio.enemyWeakened"] = "khai",
        };

        private readonly MissionDef _def;
        private readonly HashSet<RadioLineDef> _played = new();
        private readonly Dictionary<RadioTrigger, int> _generic = new();
        private readonly HashSet<RadioTrigger> _once = new();
        private readonly Random _random;
        private double _lastGeneric = -GenericGap;
        private bool _started, _ended, _bossSeen, _bossHalf, _hqHalf;

        public RadioDirector(MissionDef def, int seed)
        {
            _def = def;
            _random = new Random(seed * 31 + def.Id.GetHashCode());
        }

        /// <summary>A line to show.</summary>
        public event Action<RadioLine> Spoke;

        /// <summary>A general spoke for the first time in this battle (the camera may go to their lines).</summary>
        public event Action<string> GeneralAppeared;

        private readonly HashSet<string> _generalsHeard = new();

        /// <summary>The speaker of a text key: "radio.&lt;speaker&gt;.…", a known voice, else the brigade's HQ.</summary>
        public static string SpeakerOf(string key)
        {
            if (key == null) return "hq";
            if (Voices.TryGetValue(key, out var voice)) return voice;
            var parts = key.Split('.');
            return parts.Length > 2 && SpeakerIds.Contains(parts[1]) ? parts[1] : "hq";
        }

        public void Tick(SimWorld world, MissionSession session)
        {
            if (!_started)
            {
                _started = true;
                Trigger(world, RadioTrigger.Start, null, generic: false);
            }
            var now = world.Time;
            foreach (var line in _def.Radio)
                if (line.On == RadioTrigger.Time && now >= line.Seconds) Play(line);
            var mission = session.Mission;
            if (world.TryGetVehicle(mission.Boss, out var boss) && boss.IsAlive)
            {
                if (!_bossSeen)
                {
                    _bossSeen = true;
                    Trigger(world, RadioTrigger.Boss, null);
                }
                if (!_bossHalf && boss.Hp < boss.MaxHp * 0.5f && !mission.BossFled)
                {
                    _bossHalf = true;
                    Trigger(world, RadioTrigger.BossHalf, null);
                }
            }
            else if (!mission.Boss.IsValid) _bossSeen = _bossHalf = false;
            if (!_hqHalf && world.Bases.Of(0) is { } home && world.TryGetVehicle(home.Hq, out var hq) && !hq.Invulnerable && hq.Hp < hq.MaxHp * 0.5f)
            {
                _hqHalf = true;
                Trigger(world, RadioTrigger.HqHalf, null);
            }
            if (!_ended && session.Mode.Result is { } result)
            {
                _ended = true;
                Trigger(world, result.WinningTeam == 0 ? RadioTrigger.Win : RadioTrigger.Lose, null);
            }
        }

        /// <summary>What the battle said this step.</summary>
        public void Consume(SimWorld world, IReadOnlyList<SimEvent> events)
        {
            foreach (var e in events)
                switch (e.Kind)
                {
                    case SimEventKind.PointCaptured when e.Team == 0:
                        Trigger(world, RadioTrigger.Capture, e.DefId);
                        break;
                    case SimEventKind.PointCaptured when e.Team == 1:
                        Trigger(world, RadioTrigger.Lost, e.DefId);
                        break;
                    case SimEventKind.StageStarted when e.Value > 1f:
                        Trigger(world, RadioTrigger.Stage, e.DefId, generic: false);
                        break;
                    case SimEventKind.FortressAlert when e.DefId == "toast.enemyReinforce":
                        Trigger(world, RadioTrigger.Reinforce, null);
                        break;
                    case SimEventKind.Radio when e.DefId != null:
                        Say(e.DefId);
                        break;
                }
        }

        private void Trigger(SimWorld world, RadioTrigger trigger, string arg, bool generic = true)
        {
            var any = false;
            foreach (var line in _def.Radio)
                if (line.On == trigger && (line.Arg == null || line.Arg == arg) && Play(line)) any = true;
            if (any || !generic) return;
            // The brigade's usual chatter: not too often, and the one-off moments once.
            if (trigger is RadioTrigger.BossHalf or RadioTrigger.HqHalf or RadioTrigger.Win or RadioTrigger.Lose or RadioTrigger.Boss)
            {
                if (!_once.Add(trigger)) return;
            }
            else if (world.Time - _lastGeneric < GenericGap) return;
            var name = trigger switch
            {
                RadioTrigger.Capture => "capture",
                RadioTrigger.Lost => "lost",
                RadioTrigger.Boss => "boss",
                RadioTrigger.BossHalf => "bossHalf",
                RadioTrigger.HqHalf => "hqHalf",
                RadioTrigger.Reinforce => "reinforce",
                RadioTrigger.Win => "win",
                RadioTrigger.Lose => "lose",
                _ => null,
            };
            if (name == null) return;
            var keys = GenericKeys(name);
            if (keys.Count == 0) return;
            _generic.TryGetValue(trigger, out var n);
            _generic[trigger] = n + 1;
            _lastGeneric = world.Time;
            Say(keys[(n + _random.Next(keys.Count)) % keys.Count]);
        }

        private static readonly Dictionary<string, List<string>> GenericCache = new();

        /// <summary>The usual lines for a moment ("radio.&lt;speaker&gt;.gen.&lt;moment&gt;.&lt;n&gt;").</summary>
        private static List<string> GenericKeys(string moment)
        {
            if (GenericCache.TryGetValue(moment, out var keys)) return keys;
            keys = new List<string>();
            foreach (var key in CampaignText.Table.Keys)
                if (key.Contains(".gen." + moment + ".")) keys.Add(key);
            keys.Sort(StringComparer.Ordinal);
            GenericCache[moment] = keys;
            return keys;
        }

        private bool Play(RadioLineDef line)
        {
            if (!_played.Add(line)) return false;
            Say(line.Key);
            return true;
        }

        private void Say(string key)
        {
            var line = new RadioLine(SpeakerOf(key), key);
            Spoke?.Invoke(line);
            if (line.Enemy && _generalsHeard.Add(line.Speaker)) GeneralAppeared?.Invoke(line.Speaker);
        }
    }
}
