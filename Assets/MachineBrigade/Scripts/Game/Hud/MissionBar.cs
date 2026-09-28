using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Game.Hud
{
    /// <summary>What the HUD shows for a mode.</summary>
    public sealed class HudSpec
    {
        public HudMode Mode { get; set; } = HudMode.Score;

        /// <summary>Label over the score bars (tickets, kills, score, objectives taken).</summary>
        public string ScoreLabel { get; set; } = "stat.tickets";

        public string HintKey { get; set; } = "hint.auto";
    }

    /// <summary>
    /// The campaign's objective across the top on the kit (Field Command 2.0, G): what to do now, how
    /// far along it is (a counter and a bar), the objective chips when there are any, and the clock
    /// when the mission has one.
    /// </summary>
    internal sealed class MissionBar
    {
        private readonly Label _goal, _detail, _clock;
        private readonly KitProgress _progress;
        private readonly VisualElement _chips;
        private readonly List<PointChip> _points = new();
        private string _shownGoal, _shownDetail, _shownClock;
        private int _shownFill = -1;

        public MissionBar()
        {
            Root = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-mission-bar");
            var text = Kit.Box("fc-mission-bar__text");
            _goal = Kit.Text("", "fc-caption fc-mission-bar__goal");
            _detail = Kit.Text("", "fc-small");
            text.Add(_goal);
            text.Add(_detail);
            _progress = new KitProgress();
            _progress.AddToClassList("fc-mission-bar__progress");
            text.Add(_progress);
            Root.Add(text);
            _chips = Kit.Box("fc-score__chips");
            Root.Add(_chips);
            _clock = Kit.Text("", "fc-number-small fc-hud__clock");
            Root.Add(_clock);
        }

        public VisualElement Root { get; }

        /// <summary>An objective chip was tapped.</summary>
        public event System.Action<string> PointPressed;

        public void Update(string goal, string detail, float progress, float secondsLeft, IReadOnlyList<PointInfo> points)
        {
            if (goal != _shownGoal) _goal.text = Kit.Caps(_shownGoal = goal);
            if (detail != _shownDetail)
            {
                _detail.text = _shownDetail = detail;
                _detail.style.display = string.IsNullOrEmpty(detail) ? DisplayStyle.None : DisplayStyle.Flex;
            }
            var fill = Mathf.RoundToInt(Mathf.Clamp01(progress) * 100f);
            if (fill != _shownFill) _progress.Value = (_shownFill = fill) / 100f;
            var clock = secondsLeft < 0f ? "" : $"{(int)secondsLeft / 60}:{(int)secondsLeft % 60:00}";
            if (clock != _shownClock)
            {
                _clock.text = _shownClock = clock;
                _clock.style.display = clock.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
                _clock.EnableInClassList("fc-hud__clock--urgent", secondsLeft >= 0f && secondsLeft < 60f);
            }
            PointChip.Fill(_chips, _points, points, id => PointPressed?.Invoke(id));
            _chips.style.display = points.Count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
        }
    }

    /// <summary>
    /// A boss while it lives, on the kit (Field Command 2.0, G): its name, its health in numbers and as
    /// a bar marked where each phase begins, the phase it is in, and under them the row of its parts
    /// (prompt 9). Restyled last, its calls kept (the two Set overloads, Parts).
    /// </summary>
    internal sealed class BossBar
    {
        private readonly Label _name, _phase, _hp;
        private readonly VisualElement _fill, _track;
        private string _shownName;
        private int _shownFill = -1, _shownPhase = -1, _shownHp = -1, _shownMax = -1;
        private readonly List<VisualElement> _marks = new();

        public BossBar()
        {
            Root = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-boss");
            var head = Kit.Box("fc-boss__head");
            head.Add(Kit.Icon("skull", "fc-boss__icon"));
            _name = Kit.Text("", "fc-panel-title fc-row-text fc-boss__name");
            head.Add(_name);
            _phase = Kit.Text("", "fc-caption fc-boss__phase");
            _phase.style.display = DisplayStyle.None;
            head.Add(_phase);
            _hp = Kit.Text("", "fc-number-small fc-boss__hp");
            head.Add(_hp);
            Root.Add(head);
            _track = Kit.Box("fc-boss__track");
            _fill = Kit.Box("fc-boss__fill");
            _track.Add(_fill);
            Root.Add(_track);
            Root.Add(Parts.Root);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

        /// <summary>The boss's parts under the bar (prompt 9).</summary>
        public BossPartsRow Parts { get; } = new();

        /// <summary>
        /// A multi-phase boss: the bar marked where each phase begins (<paramref name="marks"/>, shares of full
        /// health) and "Phase n/N" beside its name; <paramref name="transforming"/> while it changes form.
        /// </summary>
        public void Set(string name, float health, int phase, IReadOnlyList<float> marks, bool transforming)
        {
            Set(name, health);
            if (name == null) return;
            var count = marks?.Count ?? 0;
            if (_marks.Count != count)
            {
                foreach (var m in _marks) m.RemoveFromHierarchy();
                _marks.Clear();
                for (var i = 0; i < count; i++)
                {
                    var mark = Kit.Box("fc-boss__mark");
                    mark.style.left = Length.Percent(marks[i] * 100f);
                    _track.Add(mark);
                    _marks.Add(mark);
                }
            }
            var shown = count == 0 ? -1 : phase + (transforming ? 1000 : 0);
            if (shown == _shownPhase) return;
            _shownPhase = shown;
            _phase.style.display = count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _phase.text = Kit.Caps(transforming ? Strings.Get("boss.transforming") : Strings.Format("boss.phase", phase + 1, count + 1));
            Root.EnableInClassList("fc-boss--transforming", transforming);
        }

        public void Set(string name, float health)
        {
            if (name == null)
            {
                if (_shownName != null) Root.style.display = DisplayStyle.None;
                _shownName = null;
                Parts.Set(null, -1);
                return;
            }
            if (name != _shownName)
            {
                _name.text = Kit.Caps(_shownName = name);
                Root.style.display = DisplayStyle.Flex;
            }
            var fill = Mathf.RoundToInt(Mathf.Clamp01(health) * 1000f);
            if (fill != _shownFill) _fill.style.width = Length.Percent((_shownFill = fill) / 10f);
        }

        /// <summary>The boss's health in numbers beside its name ("41 250 / 60 000").</summary>
        public void SetHp(float hp, float max)
        {
            var whole = Mathf.CeilToInt(Mathf.Max(0f, hp));
            var full = Mathf.CeilToInt(max);
            if (whole == _shownHp && full == _shownMax) return;
            _shownHp = whole;
            _shownMax = full;
            _hp.text = full > 0 ? $"{Kit.Count(whole)} / {Kit.Count(full)}" : "";
        }
    }
}
