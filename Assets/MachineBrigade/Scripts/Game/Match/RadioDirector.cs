using System;
using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// One line the director says: who speaks (a speaker id) and the text's key, and for the dialogue (prompt 23 H) how
    /// much it matters, the side it is said for (a Radio event's team), whether it opens a story moment, and the unit.
    /// </summary>
    internal readonly struct RadioLine
    {
        public RadioLine(string speaker, string key, DialoguePriority priority = DialoguePriority.Event, int team = 0, bool moment = false,
            EntityId unit = default)
        {
            Speaker = speaker;
            Key = key;
            Priority = priority;
            Team = team;
            Moment = moment;
            Unit = unit;
        }

        public string Speaker { get; }
        public string Key { get; }
        public DialoguePriority Priority { get; }
        public int Team { get; }
        public bool Moment { get; }
        public EntityId Unit { get; }

        /// <summary>An enemy general is speaking.</summary>
        public bool Enemy => Speaker is "varga" or "orlov" or "kessler" or "sen" or "quaden" or "aurel";
    }

    /// <summary>
    /// The battle's lines in a campaign mission: the mission's own lines when their moment
    /// comes (the start, a time, a point taken or lost, the boss arriving or half down, the HQ half
    /// down, a stage, the enemy reinforcing, the end), and when a moment has no line of its own,
    /// one of the brigade's usual ones, now and then. Radio messages the battle sends (stage events,
    /// a betrayal, a boss that flees) are spoken by whoever the key names. Each line plays once;
    /// the in-battle dialogue (prompt 23 H, <see cref="DialogueDirector"/>) decides whether and when it
    /// shows: the mission's lines at the start, a time, a stage and the end are its story beats, its
    /// other lines and the usual ones event lines, the general's answers reactions, and a Radio event's
    /// own priority is kept. Presentation only: nothing here touches the battle.
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
            _react = new ReactiveRadio(def);
            _script = ScriptText.Script.For(def.Id);
        }

        /// <summary>
        /// Prompt 30 L7: the mission's script lines. When it has any, they replace the mission's own radio lines and the
        /// usual chatter (the script keeps each mission within its line budget); the story beats of the campaign's lines
        /// (DialogueRules' moment and story keys) and the battle's Radio events still play.
        /// </summary>
        private readonly IReadOnlyList<ScriptLineDef> _script;
        private readonly HashSet<ScriptLineDef> _scriptPlayed = new();
        private readonly Dictionary<ScriptLineDef, double> _scriptLast = new();
        private bool Scripted => _script.Count > 0;

        /// <summary>Prompt 22 D.4: the general's answers to the way the player fights.</summary>
        private readonly ReactiveRadio _react;

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
            foreach (var line in _script)
                if (line.Trigger == RadioTrigger.Time && now >= line.Seconds) PlayScript(line, now);
            var mission = session.Mission;
            Watch(world, session, now);
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
                BossMarks(world, boss);
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
                if (result.WinningTeam == 0 && _react.OnWin(world.Time) is { } fast) Say(fast, DialoguePriority.Reaction);
                Trigger(world, result.WinningTeam == 0 ? RadioTrigger.Win : RadioTrigger.Lose, null);
            }
            else if (!_ended && _react.Next(world.Time) is { } answer) Say(answer, DialoguePriority.Reaction);
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
                        // The event system's priority and story moment ride on the event (DialogueRules.FromEvent).
                        var heard = DialogueRules.FromEvent(e.DefId, e.Team, e.Value, e.Mount, e.Entity, _def.General);
                        Say(e.DefId, heard.Priority, e.Team, heard.Moment, e.Entity);
                        break;
                    // Prompt 22 D.4: what the general answers.
                    case SimEventKind.DeploymentQueued when e.Team == 0 && e.DefId != null && world.Catalog.Vehicles.TryGetValue(e.DefId, out var sent):
                        _react.Deployed(sent);
                        break;
                    case SimEventKind.VehicleDestroyed when e.Team == 0:
                        _react.LostOne();
                        // L2: expensive_unit_lost, at most twice a mission.
                        if (_expensiveLost < 2 && e.DefId != null && world.Catalog.Vehicles.TryGetValue(e.DefId, out var lost) &&
                            lost.BaseCp >= ExpensiveCp && Trigger(world, RadioTrigger.ExpensiveLost, e.DefId)) _expensiveLost++;
                        break;
                    case SimEventKind.VehicleSpawned when e.Team == 0 && !_allyArrived && world.TryGetVehicle(e.Entity, out var friend) && friend.Ally:
                        _allyArrived = true;
                        Trigger(world, RadioTrigger.AllyArrives, null, generic: false);
                        break;
                    case SimEventKind.BossPhase when e.Mount == 1:
                        // The boss's own phase line (MatchRunner speaks a "radio." key) wins over the script's.
                        _lastPhaseAt = world.Time;
                        _pendingHp.Clear();
                        if (e.DefId == null || !e.DefId.StartsWith("radio.", StringComparison.Ordinal))
                            Trigger(world, RadioTrigger.BossPhase, ((int)e.Value).ToString(), generic: false);
                        break;
                    case SimEventKind.PartBroken when e.Team == 1 && world.Time - _lastPhaseAt > BossOverlap:
                        Trigger(world, RadioTrigger.BossPart, e.DefId, generic: false);
                        break;
                    case SimEventKind.BigAttack when e.Team == 1 && !_superweaponSaid:
                        // The first warning: the line that says how to get clear (P1); the warning itself is the HUD's (P0).
                        _superweaponSaid = Trigger(world, RadioTrigger.Superweapon, e.DefId, generic: false);
                        _lastPhaseAt = Math.Max(_lastPhaseAt, world.Time);
                        break;
                    case SimEventKind.NeutralCaptured when e.Team == 0 && world.Time - _neutralAt >= 30.0:
                        // Prompt 30 L6: neutral_captured (30 s apart), Arg the site's kind.
                        if (Trigger(world, RadioTrigger.NeutralCaptured, e.DefId, generic: false)) _neutralAt = world.Time;
                        break;
                    case SimEventKind.EventNotice when e.DefId != null && _eventsSeen.Add(e.NoticeKind.ToString()):
                        Trigger(world, RadioTrigger.EventTriggered, e.NoticeKind.ToString(), generic: false);
                        break;
                    case SimEventKind.BigAttack when e.Mount == 2:
                        _react.Interrupted();
                        break;
                }
        }

        private bool Trigger(SimWorld world, RadioTrigger trigger, string arg, bool generic = true)
        {
            var any = false;
            foreach (var line in _def.Radio)
                if (line.On == trigger && (line.Arg == null || line.Arg == arg) && (!Scripted || DialogueRules.IsStoryBeat(line.Key)) && Play(line)) any = true;
            if (Scripted)
            {
                foreach (var line in _script)
                    if (line.Trigger == trigger && (line.Arg == null || line.Arg == arg) && PlayScript(line, world.Time)) any = true;
                return any;
            }
            if (any || !generic) return any;
            // The brigade's usual chatter: not too often, and the one-off moments once.
            if (trigger is RadioTrigger.BossHalf or RadioTrigger.HqHalf or RadioTrigger.Win or RadioTrigger.Lose or RadioTrigger.Boss)
            {
                if (!_once.Add(trigger)) return false;
            }
            else if (world.Time - _lastGeneric < GenericGap) return false;
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
            if (name == null) return false;
            var keys = GenericKeys(name);
            if (keys.Count == 0) return false;
            _generic.TryGetValue(trigger, out var n);
            _generic[trigger] = n + 1;
            _lastGeneric = world.Time;
            // L12: the usual chatter is a tactical reaction (P3).
            Say(keys[(n + _random.Next(keys.Count)) % keys.Count], DialoguePriority.Reaction);
            return true;
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
            Say(line.Key, PriorityOf(line.On));
            return true;
        }

        // ------------------------------------------------------------------------------------------------ prompt 30 L2

        /// <summary>expensive_unit_lost: a vehicle of at least this base CP (sheet "Điểm kích hoạt").</summary>
        public const int ExpensiveCp = 15;

        /// <summary>Boss lines: a health mark within this long of a phase change (before or after) is skipped; a part line too.</summary>
        public const double BossOverlap = 10.0;

        /// <summary>objective_stall_90s: this long without progress and without a P0-P2 line.</summary>
        public const double StallSeconds = 90.0;

        /// <summary>momentum_high_once: the army at least this many times the enemy's for <see cref="MomentumSeconds"/>, the goal half done.</summary>
        public const float MomentumRatio = 2f;

        public const double MomentumSeconds = 30.0;

        private readonly HashSet<string> _marks = new(), _eventsSeen = new(), _typesSeen = new();
        private readonly List<(string mark, double at)> _pendingHp = new();
        private double _lastPhaseAt = double.NegativeInfinity, _lastProgressAt, _lastImportantAt, _momentumSince = -1, _tacticSeenAt = double.NegativeInfinity;
        private double _lastTacticSwitch = double.NegativeInfinity;
        private float _lastProgress = -1f;
        private int _expensiveLost;
        private double _neutralAt = double.NegativeInfinity;
        private bool _allyArrived, _superweaponSaid, _stallSaid, _criticalSaid, _momentumSaid, _timerSaid;

        /// <summary>The goal marks, the stall, the critical moment, the momentum, the last minute, units first seen, the general's tactic.</summary>
        private void Watch(SimWorld world, MissionSession session, double now)
        {
            var mission = session.Mission;
            if (mission == null || _ended) return;
            var progress = mission.Progress(world);
            if (progress > _lastProgress + 1e-3f)
            {
                _lastProgress = progress;
                _lastProgressAt = now;
            }
            foreach (var (mark, at) in new[] { ("1/3", 1f / 3f), ("1/2", 0.5f), ("2/3", 2f / 3f) })
                if (progress >= at && _marks.Add("p" + mark)) Trigger(world, RadioTrigger.ObjectiveProgress, mark, generic: false);
            var (done, needed) = mission.Count(world);
            if (needed > 1 && needed - done == 1 && _marks.Add("plast")) Trigger(world, RadioTrigger.ObjectiveProgress, "last", generic: false);
            if (!_stallSaid && now - Math.Max(_lastProgressAt, _lastImportantAt) >= StallSeconds && now > StallSeconds)
                _stallSaid = Trigger(world, RadioTrigger.ObjectiveStall, null, generic: false);
            if (!_criticalSaid && mission.CriticalFailure(world)) _criticalSaid = Trigger(world, RadioTrigger.Critical, null, generic: false);
            var left = mission.SecondsLeft(world);
            if (!_timerSaid && left > 0f && left <= 60f) _timerSaid = Trigger(world, RadioTrigger.Timer60, null, generic: false);
            if (!_momentumSaid && UnityEngine.Time.frameCount % 30 == 0) Momentum(world, progress, now);
            if (UnityEngine.Time.frameCount % 20 == 0) SeenTypes(world);
            if (world.AiCommanders.TryGetValue(1, out var general) && general.LastSwitchAt > _lastTacticSwitch && general.TacticSeenBy(world, 0))
            {
                _lastTacticSwitch = general.LastSwitchAt;
                if (now - _tacticSeenAt >= 45.0 && Trigger(world, RadioTrigger.TacticChange, general.Tactic, generic: false)) _tacticSeenAt = now;
            }
            for (var i = _pendingHp.Count - 1; i >= 0; i--)
                if (now - _pendingHp[i].at >= BossOverlap)
                {
                    if (now - _lastPhaseAt > BossOverlap * 2) Trigger(world, RadioTrigger.BossHp, _pendingHp[i].mark, generic: false);
                    _pendingHp.RemoveAt(i);
                }
        }

        /// <summary>boss_hp marks: held for 10 s and dropped if a phase change comes within 10 s either side.</summary>
        private void BossMarks(SimWorld world, Sim.Entities.Vehicle boss)
        {
            foreach (var mark in new[] { 75, 50, 25 })
                if (boss.Hp < boss.MaxHp * mark / 100f && _marks.Add("hp" + mark) && world.Time - _lastPhaseAt > BossOverlap)
                    _pendingHp.Add((mark.ToString(), world.Time));
        }

        private void Momentum(SimWorld world, float progress, double now)
        {
            if (!world.TryGetEconomy(0, out var ours) || !world.TryGetEconomy(1, out var theirs)) return;
            var ahead = progress >= 0.5f && ours.ArmyCp >= MomentumRatio * Math.Max(1, theirs.ArmyCp);
            if (!ahead) _momentumSince = -1;
            else if (_momentumSince < 0) _momentumSince = now;
            else if (now - _momentumSince >= MomentumSeconds) _momentumSaid = Trigger(world, RadioTrigger.Momentum, null, generic: false) || true;
        }

        /// <summary>first_unit_type_seen: an enemy kind the player's side sees for the first time in this battle.</summary>
        private void SeenTypes(SimWorld world)
        {
            foreach (var v in world.Vehicles)
                if (v.IsAlive && v.Team == 1 && v.IsVisibleTo(0) && _typesSeen.Add(v.Def.Id))
                    Trigger(world, RadioTrigger.FirstSeen, v.Def.Id, generic: false);
        }

        /// <summary>A script line, once (or again after 20 s for a repeating one), at its own priority.</summary>
        private bool PlayScript(ScriptLineDef line, double now)
        {
            if (line.Once && !_scriptPlayed.Add(line)) return false;
            if (!line.Once)
            {
                if (_scriptLast.TryGetValue(line, out var last) && now - last < 20.0) return false;
                _scriptLast[line] = now;
            }
            var priority = DialogueDirector.FromLevel(line.Priority);
            if (DialogueDirector.Level(priority) <= 2) _lastImportantAt = now;
            Say(line.Key, priority);
            return true;
        }

        /// <summary>A mission line's priority: at the start, a time, a stage and the end it tells the story; otherwise it answers an event.</summary>
        public static DialoguePriority PriorityOf(RadioTrigger trigger) =>
            trigger is RadioTrigger.Start or RadioTrigger.Time or RadioTrigger.Stage or RadioTrigger.Win or RadioTrigger.Lose
                ? DialoguePriority.Story
                : DialoguePriority.Event;

        private void Say(string key, DialoguePriority priority, int team = 0, bool moment = false, EntityId unit = default)
        {
            var line = new RadioLine(SpeakerOf(key), key, priority, team, moment, unit);
            Spoke?.Invoke(line);
            if (DialogueRules.IsEnemy(line.Speaker, _def.General, team) && _generalsHeard.Add(line.Speaker)) GeneralAppeared?.Invoke(line.Speaker);
        }
    }
}
