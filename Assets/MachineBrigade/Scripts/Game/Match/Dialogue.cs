using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>Prompt 23 H.3: how much a line matters. Lower is more important.</summary>
    public enum DialoguePriority
    {
        /// <summary>A story beat the player must hear (a betrayal, a surrender): always shown, queued, never dropped.</summary>
        Story = 0,

        /// <summary>A line that comes with a warning (before a strike, a boss's big attack): queued, and cuts chatter short.</summary>
        Warning = 1,

        /// <summary>A line as something happens (a general arrives, a boss changes phase, reinforcements): now or never.</summary>
        Event = 2,

        /// <summary>A general answering the way the player fights (prompt 22 D.4): now or never, and rarer in boss battles.</summary>
        Reaction = 3,
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
    /// Prompt 23 H.3-H.9: every character's line in a battle goes through here, one at a time. Story and warning lines
    /// queue (story first); a waiting warning cuts a chatter line short. Event and reaction lines show now or never: when
    /// nothing is up or waiting and at least <see cref="Gap"/> seconds after the last one started (reactions wait
    /// <see cref="BossReactionGap"/> while a boss is on the field). A line stays 3 to 6 s by its length, then fades; the next
    /// waits for the fade. The last <see cref="LogSize"/> lines shown are kept for the pause menu's log. A story moment
    /// slows the battle to <see cref="MomentScale"/> while its lines play (<see cref="TimeScale"/>; the runner applies it
    /// to the step rate, so the simulation and its replays are untouched). The clock is the caller's: seconds that stop
    /// under the pause. Presentation only: nothing here touches the battle.
    /// </summary>
    public sealed class DialogueDirector
    {
        public const double Gap = 9.0;
        public const double BossReactionGap = 20.0;
        public const double MinSeconds = 3.0, MaxSeconds = 6.0;

        /// <summary>The strip's fade (Screens.uss .fc-dialogue); the next line starts after it.</summary>
        public const double FadeSeconds = 0.25;

        /// <summary>A chatter line cut short by a waiting warning still shows this long.</summary>
        public const double MinShown = 1.0;

        /// <summary>A warning that could not start within this long is stale and dropped.</summary>
        public const double WarningShelf = 12.0;

        public const int LogSize = 20, QueueSize = 6;

        public const float MomentScale = 0.5f;

        /// <summary>A story moment holds at most this many lines and this long.</summary>
        public const int MomentLines = 3;

        public const double MomentMax = 14.0, MomentEaseIn = 0.4, MomentEaseOut = 0.6;

        private readonly List<(DialogueLine line, double at)> _queue = new();
        private readonly List<DialogueEntry> _log = new();
        private DialogueLine _current;
        private bool _showing;
        private double _shownAt, _until, _freeAt = double.MinValue, _lastChatter = double.MinValue;
        private double _momentStart = double.MinValue, _momentEnd = double.MinValue;
        private int _momentCount;
        private long _started;

        public DialogueSetting Setting { get; set; } = DialogueSetting.Full;

        /// <summary>A boss is on the field (reactions are rarer).</summary>
        public bool BossBattle { get; set; }

        /// <summary>A line starts showing.</summary>
        public event Action<DialogueLine> Shown;

        /// <summary>The line on show ends (it fades out).</summary>
        public event Action Hidden;

        /// <summary>H.9: a speaker starts (true) or stops speaking; the unit is theirs when the line names one.</summary>
        public event Action<string, EntityId, bool> SpeakingChanged;

        /// <summary>The line on show, if any.</summary>
        public DialogueLine? Current => _showing ? _current : null;

        /// <summary>Lines waiting (story and warning lines only).</summary>
        public int Waiting => _queue.Count;

        /// <summary>The lines shown, oldest first, at most <see cref="LogSize"/>.</summary>
        public IReadOnlyList<DialogueEntry> Log => _log;

        /// <summary>H.9: the speaker of the line on show (null: nobody is speaking).</summary>
        public string Speaker => _showing ? _current.Speaker : null;

        /// <summary>H.9: this speaker (a general's id) is speaking now; the name label on their vehicle shows a small mark.</summary>
        public bool IsSpeaking(string speaker) => _showing && speaker != null && _current.Speaker == speaker;

        /// <summary>H.9: this unit's line is on show.</summary>
        public bool IsSpeaking(EntityId unit) => _showing && unit.IsValid && _current.Unit == unit;

        /// <summary>H.7: whether a setting lets a line of this priority show.</summary>
        public static bool Allowed(DialogueSetting setting, DialoguePriority priority) =>
            priority == DialoguePriority.Story || setting == DialogueSetting.Full || setting == DialogueSetting.Important && priority == DialoguePriority.Warning;

        /// <summary>H.5: how long a line of this many letters stays: 3 s for a short one, 6 s from about 85 letters.</summary>
        public static double SecondsFor(int letters) => Math.Clamp(1.75 + letters * 0.05, MinSeconds, MaxSeconds);

        /// <summary>A line to say at <paramref name="now"/>.</summary>
        public DialogueOutcome Say(in DialogueLine line, double now)
        {
            if (line.Key == null) return DialogueOutcome.Dropped;
            if (!Allowed(Setting, line.Priority)) return DialogueOutcome.Filtered;
            if (line.Priority <= DialoguePriority.Warning)
            {
                var at = _queue.Count;
                while (at > 0 && _queue[at - 1].line.Priority > line.Priority) at--;
                _queue.Insert(at, (line, now));
                // Full: the newest warning goes (a story line never does).
                if (_queue.Count > QueueSize)
                {
                    var last = _queue.FindLastIndex(q => q.line.Priority == DialoguePriority.Warning);
                    if (last >= 0) _queue.RemoveAt(last);
                }
                var started = _started;
                Tick(now);
                return _started != started && _current.Key == line.Key ? DialogueOutcome.Shown : DialogueOutcome.Queued;
            }
            // Event and reaction lines: now or never.
            var gap = line.Priority == DialoguePriority.Reaction && BossBattle ? BossReactionGap : Gap;
            if (_showing || _queue.Count > 0 || now < _freeAt || now - _lastChatter < gap) return DialogueOutcome.Dropped;
            _lastChatter = now;
            Start(line, now);
            return DialogueOutcome.Shown;
        }

        /// <summary>Every frame: the line on show ends when its time is up (or a waiting warning cuts chatter short), and the next starts.</summary>
        public void Tick(double now)
        {
            if (_showing)
            {
                var cut = _current.Priority >= DialoguePriority.Event && now - _shownAt >= MinShown &&
                          _queue.Exists(q => q.line.Priority == DialoguePriority.Warning);
                if (now >= _until || cut) End(now);
            }
            _queue.RemoveAll(q => q.line.Priority == DialoguePriority.Warning && now - q.at > WarningShelf);
            if (!_showing && _queue.Count > 0 && now >= _freeAt)
            {
                var next = _queue[0].line;
                _queue.RemoveAt(0);
                Start(next, now);
            }
            if (MomentActive && now - _momentStart >= MomentMax) _momentEnd = _momentStart + MomentMax;
        }

        private bool MomentActive => _momentStart > double.MinValue && _momentEnd == double.MaxValue;

        private void Start(in DialogueLine line, double now)
        {
            _current = line;
            _showing = true;
            _started++;
            _shownAt = now;
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

        private void End(double now)
        {
            var line = _current;
            _showing = false;
            _freeAt = now + FadeSeconds;
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
