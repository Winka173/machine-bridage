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

        /// <summary>The compact HUD (prompt 11 A); null follows the player's setting (<see cref="Match.MatchSettings.CompactHud"/>).</summary>
        public bool? Compact { get; set; }

        /// <summary>Shows the standing hint at the start; null: only in the player's first matches (<see cref="Match.MatchSettings.ShowStartHint"/>).</summary>
        public bool? StartHint { get; set; }
    }

    /// <summary>
    /// The campaign's objective across the top on the kit (Field Command 2.0, G): what to do now, how
    /// far along it is (a counter and a bar), the objective chips when there are any, and the clock
    /// when the mission has one. Compact (prompt 11 A5): the goal and its count on one line over a thin
    /// bar, the clock at the end of the same low strip.
    /// </summary>
    internal sealed class MissionBar
    {
        private readonly Label _goal, _detail, _clock;
        private readonly KitProgress _progress;
        private readonly VisualElement _chips;
        private readonly List<PointChip> _points = new();
        private string _shownGoal, _shownDetail, _shownClock;
        private int _shownFill = -1;

        public MissionBar(bool compact = false)
        {
            Root = Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-mission-bar" + (compact ? " fc-mission-bar--compact" : ""));
            var text = Kit.Box("fc-mission-bar__text");
            var line = compact ? Kit.Box("fc-mission-bar__line") : text;
            _goal = Kit.Text("", "fc-caption fc-mission-bar__goal");
            _detail = Kit.Text("", "fc-small fc-mission-bar__detail");
            line.Add(_goal);
            line.Add(_detail);
            if (compact) text.Add(line);
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
    /// <para>
    /// Compact (prompt 11 A4): half as wide, one line of name, phase and health over a thin bar, and the
    /// parts as small icons that only show their state. A tap on the bar opens it for a few seconds at
    /// full size, where each part is a full touch target again and a tap on one still orders fire at it;
    /// it closes on its own (a part tapped keeps it open a little longer) or with another tap.
    /// </para>
    /// </summary>
    internal sealed class BossBar
    {
        /// <summary>How long the compact bar stays open after a tap.</summary>
        private const float OpenSeconds = 6f;

        private readonly Label _name, _phase, _hp, _escorts, _rank;
        private string _shownRank;
        private readonly VisualElement _escortChip;
        private int _shownEscorts = -1;

        // Prompt 18: the big attack's chip (its icon, a cooldown bar under it, lit while it charges, the seconds left).
        private readonly VisualElement _bigChip, _bigFill;
        private readonly Label _bigLabel;
        private VisualElement _bigIcon;
        private string _bigIconName;
        private int _shownBigFill = -1, _shownBigSeconds = -2;
        private bool _shownCharging;
        private readonly VisualElement _fill, _track;
        private string _shownName;
        private int _shownFill = -1, _shownPhase = -1, _shownHp = -1, _shownMax = -1;
        private readonly List<VisualElement> _marks = new();
        private readonly bool _compact;
        private float _openUntil = -1f;

        public BossBar(bool compact = false)
        {
            _compact = compact;
            Root = compact
                ? Kit.Tappable(KitPanel.SurfaceClass + " fc-surface--field fc-boss fc-boss--compact fc-boss--collapsed", Toggle)
                : Kit.Box(KitPanel.SurfaceClass + " fc-surface--field fc-boss");
            if (compact)
            {
                Root.tooltip = Strings.Get("hud.bossExpand");
                Parts.Mini = true;
                Parts.Tapped += (_, _) => _openUntil = Mathf.Max(_openUntil, Time.unscaledTime + OpenSeconds);
            }
            var head = Kit.Box("fc-boss__head");
            head.Add(Kit.Icon("skull", "fc-boss__icon"));
            // Prompt 20 F.4, G.4: "Boss" or "Mini boss" before its name.
            _rank = Kit.Text("", "fc-caption fc-boss__rank");
            _rank.style.marginRight = 6;
            _rank.style.display = DisplayStyle.None;
            head.Add(_rank);
            _name = Kit.Text("", "fc-panel-title fc-row-text fc-boss__name");
            head.Add(_name);
            _phase = Kit.Text("", "fc-caption fc-boss__phase");
            _phase.style.display = DisplayStyle.None;
            head.Add(_phase);
            _hp = Kit.Text("", "fc-number-small fc-boss__hp");
            head.Add(_hp);
            // Prompt 16 F: how many of its escorts are still alive (hidden at none).
            _escortChip = Kit.Box("fc-boss__escorts");
            _escortChip.style.flexDirection = FlexDirection.Row;
            _escortChip.style.alignItems = Align.Center;
            _escortChip.style.marginLeft = 6;
            _escortChip.Add(Kit.Icon("shield", "fc-boss__escorts-icon"));
            _escorts = Kit.Text("", "fc-number-small fc-boss__escorts-count");
            _escortChip.Add(_escorts);
            _escortChip.tooltip = Strings.Get("hud.bossEscorts");
            _escortChip.style.display = DisplayStyle.None;
            head.Add(_escortChip);
            // Prompt 18 D.1: the big attack's icon with its cooldown; lit while it charges.
            _bigChip = Kit.Box("fc-boss__big");
            _bigChip.tooltip = Strings.Get("hud.bigAttack");
            _bigLabel = Kit.Text("", "fc-number-small fc-boss__big-count");
            var bigTrack = Kit.Box("fc-boss__big-track");
            _bigFill = Kit.Box("fc-boss__big-fill");
            bigTrack.Add(_bigFill);
            _bigChip.Add(bigTrack);
            _bigChip.Add(_bigLabel);
            _bigChip.style.display = DisplayStyle.None;
            head.Add(_bigChip);
            // Prompt 19 B.5: a tiered boss's altitude now and the seconds to its next change (hidden for other bosses).
            _tierChip = Kit.Box("fc-boss__tier");
            _tierChip.style.flexDirection = FlexDirection.Row;
            _tierChip.style.alignItems = Align.Center;
            _tierChip.style.marginLeft = 6;
            _tierLabel = Kit.Text("", "fc-number-small fc-boss__tier-label");
            _tierChip.Add(_tierLabel);
            _tierChip.style.display = DisplayStyle.None;
            head.Add(_tierChip);
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

        /// <summary>The compact bar is open at full size (its parts tappable).</summary>
        public bool Expanded => _compact && !Root.ClassListContains("fc-boss--collapsed");

        /// <summary>Opens the compact bar at full size for a few seconds (a tap on it does the same).</summary>
        public void Expand()
        {
            if (!_compact) return;
            _openUntil = Time.unscaledTime + OpenSeconds;
            Root.RemoveFromClassList("fc-boss--collapsed");
            Parts.Mini = false;
        }

        private void Collapse()
        {
            _openUntil = -1f;
            Root.AddToClassList("fc-boss--collapsed");
            Parts.Mini = true;
        }

        private void Toggle()
        {
            if (Expanded) Collapse();
            else Expand();
        }

        /// <summary>Closes the open compact bar when its time is up.</summary>
        public void Tick()
        {
            if (Expanded && Time.unscaledTime > _openUntil) Collapse();
        }

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

        /// <summary>Prompt 20: its rank's label ("Boss", "Mini boss") and a mini boss's smaller bar.</summary>
        public void SetRank(MachineBrigade.Sim.Content.BossRankDef rank)
        {
            var key = rank?.Label;
            if (key == _shownRank) return;
            _shownRank = key;
            _rank.style.display = key != null ? DisplayStyle.Flex : DisplayStyle.None;
            _rank.text = key != null ? Kit.Caps(Strings.Get(key)) : "";
            Root.EnableInClassList("fc-boss--mini", rank is { Compact: true });
            // Prompt 20 O.2: the big bar for a main boss (the small one is the mini's, above).
            Root.EnableInClassList("fc-boss--main", rank is { Compact: false });
            Root.style.scale = rank is { Compact: true } ? new StyleScale(new Scale(new UnityEngine.Vector3(0.86f, 0.86f, 1f))) : StyleKeyword.Null;
        }

        /// <summary>Prompt 16 F: its escorts still alive, beside its health (none: hidden).</summary>
        public void SetEscorts(int alive)
        {
            if (alive == _shownEscorts) return;
            _shownEscorts = alive;
            _escortChip.style.display = alive > 0 ? DisplayStyle.Flex : DisplayStyle.None;
            _escorts.text = alive > 0 ? "\u00d7" + alive : "";
        }

        /// <summary>
        /// Prompt 18: the boss's big attack beside its name (null icon: none): <paramref name="ready"/> how far its
        /// cooldown has come, <paramref name="charging"/> lit while it warns, with the seconds left (negative: unknown).
        /// </summary>
        public void SetBigAttack(string icon, float ready, bool charging, float seconds)
        {
            if (icon == null)
            {
                if (_bigIconName != null) _bigChip.style.display = DisplayStyle.None;
                _bigIconName = null;
                return;
            }
            if (icon != _bigIconName)
            {
                _bigIcon?.RemoveFromHierarchy();
                _bigIcon = Kit.Icon(icon, "fc-boss__big-icon");
                _bigChip.Insert(0, _bigIcon);
                _bigIconName = icon;
                _bigChip.style.display = DisplayStyle.Flex;
            }
            var fill = Mathf.RoundToInt(Mathf.Clamp01(ready) * 20f);
            if (fill != _shownBigFill) _bigFill.style.width = Length.Percent((_shownBigFill = fill) * 5f);
            if (charging != _shownCharging)
            {
                _shownCharging = charging;
                _bigChip.EnableInClassList("fc-boss__big--charging", charging);
            }
            var whole = charging && seconds >= 0f ? Mathf.CeilToInt(seconds) : charging ? -1 : -2;
            if (whole == _shownBigSeconds) return;
            _shownBigSeconds = whole;
            _bigLabel.text = whole >= 0 ? whole.ToString() : whole == -1 ? "!" : "";
        }

        // Prompt 19 B.5: the altitude chip.
        private readonly VisualElement _tierChip;
        private readonly Label _tierLabel;
        private VisualElement _tierIcon;
        private string _tierIconName, _shownTier;

        /// <summary>Prompt 19: the boss's altitude tier beside its name (null icon: none), with the seconds to its next change in the text.</summary>
        public void SetTier(string icon, string text, string tooltip)
        {
            if (icon == null)
            {
                if (_tierIconName != null) _tierChip.style.display = DisplayStyle.None;
                _tierIconName = null;
                return;
            }
            if (icon != _tierIconName)
            {
                _tierIcon?.RemoveFromHierarchy();
                _tierIcon = Kit.Icon(icon, "fc-boss__tier-icon");
                _tierChip.Insert(0, _tierIcon);
                _tierIconName = icon;
                _tierChip.style.display = DisplayStyle.Flex;
                _tierChip.tooltip = tooltip;
            }
            if (text != _shownTier) _tierLabel.text = _shownTier = text;
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
