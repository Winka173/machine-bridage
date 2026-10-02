using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 23 H.3 / prompt 30 L12: how much a line matters, lower first. The P levels of the writing rules:
    /// <see cref="System"/> P0, <see cref="Story"/> and <see cref="Warning"/> P1, <see cref="Event"/> P2,
    /// <see cref="Reaction"/> P3, <see cref="Ambient"/> P4 (<see cref="DialogueDirector.Level"/>). The Sim's Radio
    /// events give Value = priority + 1 for Story..Reaction, so those four keep their numbers.
    /// </summary>
    public enum DialoguePriority
    {
        /// <summary>P0: a system warning (a superweapon, danger). Shown whatever the setting; cuts any line short.</summary>
        System = -1,

        /// <summary>P1: a story beat the player must hear (a betrayal, a surrender): always shown, ignores the gap, never dropped.</summary>
        Story = 0,

        /// <summary>P1: the line that comes with a warning (the first superweapon's "get clear"): ignores the gap, cuts chatter short.</summary>
        Warning = 1,

        /// <summary>P2: the mission's own event (a goal mark, a boss part, a unit first seen): waits for the gap, kept 12 s.</summary>
        Event = 2,

        /// <summary>P3: a tactical reaction (a point taken, reinforcements, a general's answer): waits for the gap, dropped after 8 s.</summary>
        Reaction = 3,

        /// <summary>P4: atmosphere (momentum, a boss's health mark): waits for the gap, dropped after 8 s.</summary>
        Ambient = 4,
    }

    /// <summary>Prompt 23 H.7: Settings, In-battle dialogue.</summary>
    public enum DialogueSetting
    {
        Full = 0,

        /// <summary>Story and warning lines only.</summary>
        Important = 1,

        /// <summary>Story lines only (they always show).</summary>
        Off = 2,
    }

    /// <summary>
    /// One line of in-battle dialogue: a text key (filled with <see cref="Arg"/> when it has a placeholder), who says it (a
    /// speaker id: a story character, a commander's portrait, "hq"), their side, how much it matters, whether it opens a
    /// story moment (H.8: the battle slows while it and the story lines after it play), and the unit that speaks, if any.
    /// The text is read when shown, so the log follows a language switch.
    /// </summary>
    public readonly struct DialogueLine
    {
        public DialogueLine(string key, DialoguePriority priority, string speaker, bool enemy, bool moment = false, EntityId unit = default, object arg = null)
        {
            Key = key;
            Priority = priority;
            Speaker = speaker;
            Enemy = enemy;
            Moment = moment;
            Unit = unit;
            Arg = arg;
        }

        public string Key { get; }
        public DialoguePriority Priority { get; }
        public string Speaker { get; }
        public bool Enemy { get; }
        public bool Moment { get; }
        public EntityId Unit { get; }
        public object Arg { get; }

        /// <summary>The words (the speaker's prefix taken off) in the current language.</summary>
        public string Words => DialogueText.Split(DialogueText.Text(Key, Arg), Speaker).words;

        /// <summary>The speaker's short name in the current language.</summary>
        public string Name => DialogueText.Name(Speaker);
    }

    /// <summary>A line the strip showed, and when (the director's clock).</summary>
    public readonly struct DialogueEntry
    {
        public DialogueEntry(DialogueLine line, double at)
        {
            Line = line;
            At = at;
        }

        public DialogueLine Line { get; }
        public double At { get; }
    }

    /// <summary>What <see cref="DialogueDirector.Say"/> did with a line.</summary>
    public enum DialogueOutcome
    {
        Shown,
        Queued,

        /// <summary>A lower line that could not show now (something else is up or waiting, or it is too soon after the last).</summary>
        Dropped,

        /// <summary>The setting hides lines of this priority.</summary>
        Filtered,
    }

    /// <summary>
    /// Prompt 23 H.3-H.9, queue rules of prompt 30 L12: every character's line in a battle goes through here, one at a
    /// time. Every line waits in one queue, most important first (<see cref="Level"/>), and starts once the line on show
    /// has faded. P0 (<see cref="DialoguePriority.System"/>) cuts any line short and shows whatever the setting; P1 (story,
    /// the warning's line) ignores the gap but waits for the line on show; P2-P4 wait until <see cref="Gap"/> seconds
    /// (<see cref="BossGap"/> with a boss on the field) after the last line started: the gap only stops lines piling up,
    /// it is not a target rhythm. A P2 line that cannot start within <see cref="EventShelf"/> s, and a P3 or P4 line within
    /// <see cref="ReactionShelf"/> s, is stale and dropped, never saved up. A waiting P1 cuts a P2-P4 line short. A line
    /// stays 3 to 6 s by its length, then fades. The last <see cref="LogSize"/> lines shown are kept for the pause menu's
    /// log. A story moment slows the battle to <see cref="MomentScale"/> while its lines play (<see cref="TimeScale"/>; the
    /// runner applies it to the step rate, so the simulation and its replays are untouched). The clock is the caller's:
    /// seconds that stop under the pause. Presentation only: nothing here touches the battle.
    /// </summary>
    public sealed class DialogueDirector
    {
        public const double Gap = 9.0;

        /// <summary>The gap while a boss is on the field (L12: 20 s).</summary>
        public const double BossGap = 20.0;

        /// <summary>The old name of <see cref="BossGap"/>.</summary>
        public const double BossReactionGap = BossGap;

        public const double MinSeconds = 3.0, MaxSeconds = 6.0;

        /// <summary>The strip's fade (Screens.uss .fc-dialogue); the next line starts after it.</summary>
        public const double FadeSeconds = 0.25;

        /// <summary>A lower line cut short by a waiting P0 or P1 line still shows this long (a P0 cuts at once).</summary>
        public const double MinShown = 1.0;

        /// <summary>A P1 warning line that could not start within this long is stale and dropped (a story line never is).</summary>
        public const double WarningShelf = 12.0;

        /// <summary>P2: dropped when it could not start within this long.</summary>
        public const double EventShelf = 12.0;

        /// <summary>P3 and P4: dropped when they could not start within this long (L12: 8 s).</summary>
        public const double ReactionShelf = 8.0;

        public const int LogSize = 20, QueueSize = 6;

        public const float MomentScale = 0.5f;

        /// <summary>A story moment holds at most this many lines and this long.</summary>
        public const int MomentLines = 3;

        public const double MomentMax = 14.0, MomentEaseIn = 0.4, MomentEaseOut = 0.6;

        private readonly List<(DialogueLine line, double at, long order)> _queue = new();
        private readonly List<DialogueEntry> _log = new();
        private DialogueLine _current;
        private bool _showing;
        private double _shownAt, _until, _freeAt = double.MinValue, _lastStart = double.MinValue;
        private double _momentStart = double.MinValue, _momentEnd = double.MinValue;
        private int _momentCount;
        private long _started, _arrivals;

        public DialogueSetting Setting { get; set; } = DialogueSetting.Full;

        /// <summary>A boss is on the field (the gap is longer).</summary>
        public bool BossBattle { get; set; }

        /// <summary>A line starts showing.</summary>
        public event Action<DialogueLine> Shown;

        /// <summary>The line on show ends (it fades out).</summary>
        public event Action Hidden;

        /// <summary>H.9: a speaker starts (true) or stops speaking; the unit is theirs when the line names one.</summary>
        public event Action<string, EntityId, bool> SpeakingChanged;

        /// <summary>The line on show, if any.</summary>
        public DialogueLine? Current => _showing ? _current : null;

        /// <summary>Lines waiting.</summary>
        public int Waiting => _queue.Count;

        /// <summary>The lines shown, oldest first, at most <see cref="LogSize"/>.</summary>
        public IReadOnlyList<DialogueEntry> Log => _log;

        /// <summary>H.9: the speaker of the line on show (null: nobody is speaking).</summary>
        public string Speaker => _showing ? _current.Speaker : null;

        /// <summary>H.9: this speaker (a general's id) is speaking now; the name label on their vehicle shows a small mark.</summary>
        public bool IsSpeaking(string speaker) => _showing && speaker != null && _current.Speaker == speaker;

        /// <summary>H.9: this unit's line is on show.</summary>
        public bool IsSpeaking(EntityId unit) => _showing && unit.IsValid && _current.Unit == unit;

        /// <summary>L12: a priority's P level (0 system warning, 1 story and the warning's line, 2 event, 3 reaction, 4 atmosphere).</summary>
        public static int Level(DialoguePriority priority) => priority switch
        {
            DialoguePriority.System => 0,
            DialoguePriority.Story or DialoguePriority.Warning => 1,
            DialoguePriority.Event => 2,
            DialoguePriority.Reaction => 3,
            _ => 4,
        };

        /// <summary>The P level of a script line's priority number (1-4); 0 stays a system warning.</summary>
        public static DialoguePriority FromLevel(int level) => level switch
        {
            <= 0 => DialoguePriority.System,
            1 => DialoguePriority.Story,
            2 => DialoguePriority.Event,
            3 => DialoguePriority.Reaction,
            _ => DialoguePriority.Ambient,
        };

        /// <summary>H.7 / L12: whether a setting lets a line of this priority show. P0 and story lines always do.</summary>
        public static bool Allowed(DialogueSetting setting, DialoguePriority priority) =>
            priority is DialoguePriority.System or DialoguePriority.Story || setting == DialogueSetting.Full ||
            setting == DialogueSetting.Important && priority == DialoguePriority.Warning;

        /// <summary>H.5: how long a line of this many letters stays: 3 s for a short one, 6 s from about 85 letters.</summary>
        public static double SecondsFor(int letters) => Math.Clamp(1.75 + letters * 0.05, MinSeconds, MaxSeconds);

        /// <summary>How long a line may wait before it is stale (a story line never is).</summary>
        public static double Shelf(DialoguePriority priority) => priority switch
        {
            DialoguePriority.System or DialoguePriority.Story => double.PositiveInfinity,
            DialoguePriority.Warning => WarningShelf,
            DialoguePriority.Event => EventShelf,
            _ => ReactionShelf,
        };

        /// <summary>A line to say at <paramref name="now"/>.</summary>
        public DialogueOutcome Say(in DialogueLine line, double now)
        {
            if (line.Key == null) return DialogueOutcome.Dropped;
            if (!Allowed(Setting, line.Priority)) return DialogueOutcome.Filtered;
            var order = ++_arrivals;
            // By priority (a story line before a warning's line of the same level), then by arrival.
            var at = _queue.Count;
            while (at > 0 && _queue[at - 1].line.Priority > line.Priority) at--;
            _queue.Insert(at, (line, now, order));
            // Full: the newest of the least important goes (never P0 or a story line).
            if (_queue.Count > QueueSize)
            {
                var drop = -1;
                for (var i = _queue.Count - 1; i >= 0; i--)
                    if (Level(_queue[i].line.Priority) >= 1 && _queue[i].line.Priority != DialoguePriority.Story &&
                        (drop < 0 || Level(_queue[i].line.Priority) > Level(_queue[drop].line.Priority)))
                        drop = i;
                if (drop >= 0)
                {
                    var dropped = _queue[drop].order == order;
                    _queue.RemoveAt(drop);
                    if (dropped) return DialogueOutcome.Dropped;
                }
            }
            var started = _started;
            Tick(now);
            return _started != started && _current.Key == line.Key ? DialogueOutcome.Shown : DialogueOutcome.Queued;
        }

        /// <summary>Every frame: stale lines go, the line on show ends when its time is up (or a waiting P0/P1 cuts it), and the next starts.</summary>
        public void Tick(double now)
        {
            if (MomentActive && now - _momentStart >= MomentMax) _momentEnd = _momentStart + MomentMax;
            _queue.RemoveAll(q => now - q.at > Shelf(q.line.Priority));
            if (_showing)
            {
                var level = Level(_current.Priority);
                var cut = _queue.Count > 0 && (
                    Level(_queue[0].line.Priority) == 0 && level > 0 ||
                    Level(_queue[0].line.Priority) == 1 && level >= 2 && now - _shownAt >= MinShown);
                if (now >= _until || cut) End(now, cut && Level(_queue[0].line.Priority) == 0);
            }
            if (_showing || _queue.Count == 0) return;
            var next = _queue[0].line;
            var nextLevel = Level(next.Priority);
            // P0 starts at once; the others after the fade; P2-P4 also after the gap.
            if (nextLevel > 0 && now < _freeAt) return;
            if (nextLevel >= 2 && now - _lastStart < (BossBattle ? BossGap : Gap)) return;
            _queue.RemoveAt(0);
            Start(next, now);
        }

        private bool MomentActive => _momentStart > double.MinValue && _momentEnd == double.MaxValue;

        private void Start(in DialogueLine line, double now)
        {
            _current = line;
            _showing = true;
            _started++;
            _shownAt = now;
            _lastStart = now;
            _until = now + SecondsFor(line.Words.Length + line.Name.Length);
            _log.Add(new DialogueEntry(line, now));
            if (_log.Count > LogSize) _log.RemoveAt(0);
            if (line.Moment && !MomentActive)
            {
                _momentStart = now;
                _momentEnd = double.MaxValue;
                _momentCount = 1;
            }
            else if (MomentActive) _momentCount++;
            Shown?.Invoke(line);
            SpeakingChanged?.Invoke(line.Speaker, line.Unit, true);
        }

        private void End(double now, bool system = false)
        {
            var line = _current;
            _showing = false;
            _freeAt = system ? now : now + FadeSeconds;
            // A story moment lasts while story lines follow one another, up to three of them.
            if (MomentActive && (_momentCount >= MomentLines || _queue.Count == 0 || _queue[0].line.Priority != DialoguePriority.Story))
                _momentEnd = now;
            Hidden?.Invoke();
            SpeakingChanged?.Invoke(line.Speaker, line.Unit, false);
        }

        /// <summary>H.8: the battle's pace now: 1, or down to <see cref="MomentScale"/> during a story moment (eased in and out).</summary>
        public float TimeScale(double now)
        {
            if (_momentStart == double.MinValue || now < _momentStart) return 1f;
            if (now < _momentEnd)
                return Lerp(1f, MomentScale, Smooth((now - _momentStart) / MomentEaseIn));
            return Lerp(MomentScale, 1f, Smooth((now - _momentEnd) / MomentEaseOut));
        }

        private static float Lerp(float a, float b, float t) => a + (b - a) * t;

        private static float Smooth(double x)
        {
            var t = (float)Math.Clamp(x, 0.0, 1.0);
            return t * t * (3f - 2f * t);
        }
    }

    /// <summary>
    /// Prompt 23 H.1: how today's lines enter the dialogue. A line's priority when the battle does not give one, its speaker
    /// (the key's, else a prefix in its text), its side, and the story moments (H.8). The event system gives a priority in
    /// a Radio event (see <see cref="FromEvent"/>).
    /// </summary>
    public static class DialogueRules
    {
        /// <summary>The generals who are always the enemy's; the others (Brandt, Venn, Thorne) are when they lead the mission's enemy or speak for the enemy's side.</summary>
        private static readonly HashSet<string> Enemies = new() { "varga", "orlov", "kessler", "aurel", "quaden" };

        /// <summary>
        /// H.8's data hook by line: the story beats that slow the battle, six in the campaign (prompt 23 E): Varga's word at the
        /// Hollow Dam (c6m14), Venn losing her swarm (c5m10), Thorne's betrayal (c7m10), Thorne on Typhon's bridge (c9m10),
        /// Varga's fall (c12m10) and Icarus falling (c12m10). The lines queued right after each (StoryKeys) play in the moment.
        /// </summary>
        public static readonly HashSet<string> MomentKeys = new()
        {
            "radio.varga.c6m14.1", "radio.sen.c5m10.s3", "radio.linh.c7m10.s6", "radio.betrayal", "radio.hung.c9m10.s4",
            "radio.varga.c12m10.s4e", "radio.aurel.bug.crash",
        };

        /// <summary>The story beats among today's lines (the event system gives its own a priority): the moments and the lines that answer them.</summary>
        public static readonly HashSet<string> StoryKeys = new()
        {
            "radio.betrayal", "radio.sen.c5m10.s3", "radio.khai.c5m10.s3b", "radio.linh.c7m10.s6", "radio.hung.c7m10.s4", "radio.khai.c7m10.s4",
            "radio.hung.c9m10.s4", "radio.linh.c9m10.s4b", "radio.varga.c12m10.s4e", "radio.linh.c12m10.s5", "radio.aurel.bug.crash",
            "radio.aurel.bug.down",
        };

        /// <summary>A story beat or a moment's line: kept when a mission's script replaces its radio lines (prompt 30 L7).</summary>
        public static bool IsStoryBeat(string key) => key != null && (MomentKeys.Contains(key) || StoryKeys.Contains(key));

        /// <summary>A line's priority by its key: a story beat, a warning (a boss's big attack, a key with ".warn"), else an event line.</summary>
        public static DialoguePriority PriorityOf(string key)
        {
            if (key == null) return DialoguePriority.Event;
            if (StoryKeys.Contains(key)) return DialoguePriority.Story;
            if (key.StartsWith("radio.bigattack.", StringComparison.Ordinal) || key.Contains(".warn")) return DialoguePriority.Warning;
            if (key.Contains(".react.")) return DialoguePriority.Reaction;
            return DialoguePriority.Event;
        }

        /// <summary>Whether a speaker speaks for the enemy: an enemy general, the mission's general, or anyone else on the enemy's side (but Command).</summary>
        public static bool IsEnemy(string speaker, string general, int team)
        {
            if (speaker is null or "hq" or "recon") return false;
            return Enemies.Contains(speaker) || speaker == general || team == 1;
        }

        /// <summary>A line from a key: its speaker (a prefix in the text names one, else the key's), side, priority and moment.</summary>
        public static DialogueLine Line(string key, DialoguePriority? priority = null, string general = null, int team = 0, bool moment = false,
            EntityId unit = default, object arg = null, string speaker = null)
        {
            speaker ??= RadioDirector.SpeakerOf(key);
            speaker = DialogueText.Split(DialogueText.Text(key, arg), speaker).speaker;
            return new DialogueLine(key, priority ?? PriorityOf(key), speaker, IsEnemy(speaker, general, team), moment || MomentKeys.Contains(key), unit, arg);
        }

        /// <summary>
        /// A line from the battle's Radio event: <paramref name="key"/> is its DefId and <paramref name="team"/> its Team.
        /// The event system's contract: Value = priority + 1 (1 story, 2 warning, 3 event, 4 reaction; 0 leaves it to the
        /// key), Mount = 1 opens a story moment, Entity = the unit that speaks (or none).
        /// </summary>
        public static DialogueLine FromEvent(string key, int team, float value, int mount, EntityId unit, string general)
        {
            var level = (int)Math.Round(value);
            DialoguePriority? priority = level is >= 1 and <= 4 ? (DialoguePriority)(level - 1) : null;
            return Line(key, priority, general, team, (mount & 1) == 1, unit);
        }
    }
}
