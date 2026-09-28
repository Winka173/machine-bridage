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
    /// The campaign's top-bar objective: what to do, how far along it is (a counter and a bar),
    /// the objective chips when there are any, and the clock when the mission has one.
    /// </summary>
    internal sealed class MissionBar
    {
        private readonly Label _goal, _detail, _clock;
        private readonly VisualElement _fill, _chips;
        private readonly List<PointChip> _points = new();
        private string _shownGoal, _shownDetail, _shownClock;
        private int _shownFill = -1;

        public MissionBar()
        {
            Root = UiKit.Box("mission-bar");
            var text = UiKit.Box("mission-bar-text");
            _goal = UiKit.Text("", "mission-goal");
            _detail = UiKit.Text("", "mission-detail");
            text.Add(_goal);
            text.Add(_detail);
            Root.Add(text);
            var track = UiKit.Box("mission-track");
            _fill = UiKit.Box("mission-fill");
            track.Add(_fill);
            Root.Add(track);
            _chips = UiKit.Box("chips mission-chips");
            Root.Add(_chips);
            _clock = UiKit.Text("", "mission-clock");
            Root.Add(_clock);
        }

        public VisualElement Root { get; }

        /// <summary>An objective chip was tapped.</summary>
        public event System.Action<string> PointPressed;

        public void Update(string goal, string detail, float progress, float secondsLeft, IReadOnlyList<PointInfo> points)
        {
            if (goal != _shownGoal) _goal.text = _shownGoal = goal;
            if (detail != _shownDetail) _detail.text = _shownDetail = detail;
            var fill = Mathf.RoundToInt(Mathf.Clamp01(progress) * 100f);
            if (fill != _shownFill) _fill.style.width = Length.Percent(_shownFill = fill);
            var clock = secondsLeft < 0f ? "" : $"{(int)secondsLeft / 60}:{(int)secondsLeft % 60:00}";
            if (clock != _shownClock)
            {
                _clock.text = _shownClock = clock;
                _clock.style.display = clock.Length > 0 ? DisplayStyle.Flex : DisplayStyle.None;
                _clock.EnableInClassList("urgent", secondsLeft >= 0f && secondsLeft < 60f);
            }
            while (_points.Count < points.Count)
            {
                var chip = new PointChip();
                chip.AddManipulator(new Tap(() =>
                {
                    if (chip.Id != null) PointPressed?.Invoke(chip.Id);
                }));
                _chips.Add(chip);
                _points.Add(chip);
            }
            for (var i = 0; i < points.Count; i++) _points[i].Set(points[i]);
        }
    }

    /// <summary>A boss's name and health across the top of the screen while it lives.</summary>
    internal sealed class BossBar
    {
        private readonly Label _name, _phase;
        private readonly VisualElement _fill, _track;
        private string _shownName;
        private int _shownFill = -1, _shownPhase = -1;
        private readonly List<VisualElement> _marks = new();

        public BossBar()
        {
            Root = UiKit.Box("boss-bar");
            var head = UiKit.Box("boss-head");
            head.Add(UiKit.Icon("skull", UiKit.Ink, 1.8f));
            _name = UiKit.Text("", "boss-name");
            head.Add(_name);
            _phase = UiKit.Text("", "boss-phase");
            _phase.style.display = DisplayStyle.None;
            head.Add(_phase);
            Root.Add(head);
            _track = UiKit.Box("boss-track");
            _fill = UiKit.Box("boss-fill");
            _track.Add(_fill);
            Root.Add(_track);
            Root.style.display = DisplayStyle.None;
        }

        public VisualElement Root { get; }

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
                    var mark = UiKit.Box("boss-mark");
                    mark.style.left = Length.Percent(marks[i] * 100f);
                    _track.Add(mark);
                    _marks.Add(mark);
                }
            }
            var shown = count == 0 ? -1 : phase + (transforming ? 1000 : 0);
            if (shown == _shownPhase) return;
            _shownPhase = shown;
            _phase.style.display = count > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _phase.text = transforming ? Strings.Get("boss.transforming") : Strings.Format("boss.phase", phase + 1, count + 1);
            Root.EnableInClassList("transforming", transforming);
        }

        public void Set(string name, float health)
        {
            if (name == null)
            {
                if (_shownName != null) Root.style.display = DisplayStyle.None;
                _shownName = null;
                return;
            }
            if (name != _shownName)
            {
                _name.text = _shownName = name;
                Root.style.display = DisplayStyle.Flex;
            }
            var fill = Mathf.RoundToInt(Mathf.Clamp01(health) * 1000f);
            if (fill != _shownFill) _fill.style.width = Length.Percent((_shownFill = fill) / 10f);
        }
    }
}
